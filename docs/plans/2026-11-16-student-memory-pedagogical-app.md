# Plan de Proyecto: Plataforma de Gestión de Alumnos Particulares y Memoria Pedagógica

**Fecha:** 2026-11-16  
**Estado:** Pendiente de aprobación explícita (Fase 3)  
**Restricción clave:** 0 % dependencia de LLMs externos. Todo el diagnóstico y personalización funciona mediante código OOP determinista y modelos ML clásicos entrenables localmente.

---

## 1. Decisiones Cerradas (Resultado del Grill-Me)

| Dimensión | Decisión Acordada |
| :--- | :--- |
| **Stack Backend** | Python 3.12+, FastAPI, OOP estricto, `pytest`, `mypy` (strict) |
| **Stack Frontend** | React + TypeScript, Vite, `Vitest`, `@testing-library/react` |
| **Persistencia y Uso** | Monousuario local (1 profesor) sobre SQLite, sin auth en MVP, aislado tras *Repository Pattern* (migrable a PostgreSQL) |
| **Taxonomía Académica** | Catálogo compartido gestionado por el profesor: `Asignatura -> Tema -> Tipo de Ejercicio` |
| **Memoria del Alumno** | Perfil (`Student`) + Objetivos/Exámenes con fecha límite (`ExamGoal`) + Sesiones (`TutoringSession`) con intentos individuales (`ExerciseAttempt`: `SUCCESS`/`PARTIAL`/`FAILURE` + causa del error) |
| **Motor Analítico** | Puerto `PedagogicalAnalyzerPort` (Patrón Strategy): `HeuristicPedagogicalAnalyzer` en MVP + adaptador preparado para `scikit-learn` (`SklearnPedagogicalAnalyzer`) |
| **Salidas del Diagnóstico** | (1) Ranking de asignaturas/temas prioritarios con score y motivos explicables, (2) Top tipos de ejercicio con mayor fallo y causa dominante, (3) Tendencia evolutiva y alertas de examen próximo |
| **Fuera del MVP** | Pagos/facturación, calendario externo, exportación PDF, portal de alumnos/padres, multiusuario |

---

## 2. Arquitectura del Proyecto (Clean Architecture & OOP)

```text
Clases/
├── docs/
│   └── plans/
│       └── 2026-11-16-student-memory-pedagogical-app.md
├── backend/
│   ├── pyproject.toml
│   ├── src/
│   │   └── tutoring/
│   │       ├── domain/                 # Núcleo OOP puro (0 dependencias externas)
│   │       │   ├── entities/           # Student, TutoringSession, Subject, Topic, ExerciseType
│   │       │   ├── value_objects/      # StudentId, ExamGoal, ExerciseAttempt, StudentDiagnostic...
│   │       │   ├── enums.py            # AttemptOutcome, ErrorCause, LearningTrend
│   │       │   ├── exceptions.py       # DomainError, InvalidAttemptError, EntityNotFoundError
│   │       │   ├── ports/              # ABC/Protocol: Repositories + PedagogicalAnalyzerPort
│   │       │   └── analytics/          # HeuristicPedagogicalAnalyzer + FeatureExtractor
│   │       ├── application/            # Casos de uso (orquestación, transacciones)
│   │       │   ├── dtos.py
│   │       │   └── use_cases/          # ManageStudents, ManageCatalog, RecordSession, GetDiagnostic
│   │       ├── infrastructure/         # SQLite Repositories, Mappers, ML Adapter (scikit-learn)
│   │       │   ├── persistence/
│   │       │   └── ml/
│   │       └── presentation/           # FastAPI App, Routers, Pydantic Schemas, Dependency Injection
│   │           └── api/
│   └── tests/
│       ├── unit/                       # Domain, Analytics y Application (con In-Memory Fakes)
│       └── integration/                # SQLite Repositories y FastAPI endpoints
└── frontend/
    ├── package.json
    ├── tsconfig.json
    └── src/
        ├── api/                        # Cliente HTTP tipado (mockeable en tests UI)
        ├── domain/                     # Tipos TS espejados del contrato OpenAPI
        ├── components/                 # Componentes accesibles por rol/etiqueta
        ├── pages/                      # StudentsPage, StudentDetailPage, CatalogPage, RecordSessionPage
        └── tests/                      # Tests de conducta y accesibilidad (@testing-library/react)
```

---

## 3. Contratos de Interfaz y Modelo de Dominio OOP

### 3.1 Enums y Value Objects (`domain/`)

```python
from enum import Enum
from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

class AttemptOutcome(str, Enum):
    SUCCESS = "SUCCESS"   # Peso de fallo = 0.0
    PARTIAL = "PARTIAL"   # Peso de fallo = 0.5
    FAILURE = "FAILURE"   # Peso de fallo = 1.0

class ErrorCause(str, Enum):
    CONCEPT = "CONCEPT"             # No domina la teoría/concepto
    CALCULATION = "CALCULATION"     # Fallo operativo o de cálculo
    COMPREHENSION = "COMPREHENSION" # No entiende el enunciado
    CARELESSNESS = "CARELESSNESS"   # Despiste / precipitación

class LearningTrend(str, Enum):
    IMPROVING = "IMPROVING"
    STAGNANT = "STAGNANT"
    REGRESSING = "REGRESSING"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"

@dataclass(frozen=True)
class ExerciseAttempt:
    exercise_type_id: UUID
    outcome: AttemptOutcome
    error_cause: ErrorCause | None = None
    notes: str = ""
    # Invariante: si outcome == SUCCESS -> error_cause debe ser None (o rechazarse si inconsistente);
    # si outcome in (PARTIAL, FAILURE) -> se permite/recomienda error_cause válido.

@dataclass(frozen=True)
class ExamGoal:
    id: UUID
    subject_id: UUID
    title: str
    exam_date: date
    topic_ids: tuple[UUID, ...] = ()
    # Método de dominio: days_remaining(reference_date: date) -> int
```

### 3.2 Entidades Ricas (`domain/entities/`)

- **`Subject` / `Topic` / `ExerciseType` (Catálogo Taxonómico):**
  - `Subject(id, name, description)` — gestiona invariantes de nombre no vacío y unicidad lógica.
  - `Topic(id, subject_id, name)` — pertenece obligatoriamente a una `Subject`.
  - `ExerciseType(id, topic_id, name, description)` — unidad mínima evaluable compartida entre alumnos.
- **`Student` (Aggregate Root):**
  - Estado: `id`, `full_name`, `academic_level`, `pedagogical_notes`, `exam_goals: list[ExamGoal]`.
  - Comportamiento rico:
    - `add_exam_goal(goal: ExamGoal, today: date) -> None` (valida que el examen no sea incoherente o duplicado).
    - `upcoming_exams(reference_date: date, horizon_days: int = 14) -> list[ExamGoal]`.
    - `update_pedagogical_notes(notes: str) -> None`.
- **`TutoringSession` (Aggregate Root):**
  - Estado: `id`, `student_id`, `occurred_at: datetime`, `duration_minutes: int`, `session_notes: str`, `attempts: list[ExerciseAttempt]`.
  - Comportamiento rico:
    - `record_attempt(attempt: ExerciseAttempt) -> None` (valida invariantes de dominio).
    - `failure_rate() -> float` (calculada usando pesos `0.0 / 0.5 / 1.0`).

### 3.3 Contratos de Salida del Diagnóstico (`domain/value_objects/diagnostic.py`)

```python
@dataclass(frozen=True)
class SubjectPriority:
    subject_id: UUID
    subject_name: str
    priority_score: float          # [0.0 .. 100.0]
    weighted_failure_rate: float   # [0.0 .. 1.0]
    upcoming_exam_days: int | None
    trend: LearningTrend
    reasons: tuple[str, ...]       # Explicabilidad determinista legible

@dataclass(frozen=True)
class WeakExerciseType:
    exercise_type_id: UUID
    exercise_type_name: str
    topic_name: str
    subject_name: str
    attempts_count: int
    weighted_failure_rate: float
    dominant_error_cause: ErrorCause | None

@dataclass(frozen=True)
class ExamAlert:
    exam_goal_id: UUID
    subject_name: str
    title: str
    days_remaining: int
    readiness_risk: str            # "HIGH" | "MEDIUM" | "LOW"

@dataclass(frozen=True)
class StudentDiagnostic:
    student_id: UUID
    generated_at: datetime
    analyzer_name: str             # ej. "HeuristicPedagogicalAnalyzerV1"
    subject_priorities: tuple[SubjectPriority, ...]
    weak_exercise_types: tuple[WeakExerciseType, ...]
    exam_alerts: tuple[ExamAlert, ...]
    overall_trend: LearningTrend
```

### 3.4 Puertos de Dominio (`domain/ports/`)

- `StudentRepository(Protocol)`: `save(student)`, `get_by_id(id)`, `list_all()`, `delete(id)`
- `CatalogRepository(Protocol)`: `save_subject`, `save_topic`, `save_exercise_type`, `get_catalog_tree()`, `get_exercise_type(id)`, `get_subject(id)`
- `SessionRepository(Protocol)`: `save(session)`, `list_by_student(student_id)`, `get_by_id(id)`
- `PedagogicalAnalyzerPort(Protocol)`:
  ```python
  def analyze(
      self,
      student: Student,
      sessions: Sequence[TutoringSession],
      catalog: AcademicCatalogSnapshot,
      reference_date: date,
  ) -> StudentDiagnostic: ...
  ```

### 3.5 Contratos API REST (FastAPI)

| Método y Ruta | Caso de Uso | Payload / Respuesta |
| :--- | :--- | :--- |
| `GET /api/students` | Listar alumnos | `StudentSummaryDTO[]` |
| `POST /api/students` | Crear alumno | `CreateStudentDTO -> StudentDTO` |
| `GET /api/students/{id}` | Ficha completa alumno + objetivos | `StudentDetailDTO` |
| `POST /api/students/{id}/exam-goals` | Añadir examen/objetivo | `CreateExamGoalDTO -> ExamGoalDTO` |
| `GET /api/catalog` | Obtener árbol Asignatura -> Tema -> Tipo | `CatalogTreeDTO` |
| `POST /api/catalog/subjects` | Crear asignatura | `CreateSubjectDTO -> SubjectDTO` |
| `POST /api/catalog/topics` | Crear tema bajo asignatura | `CreateTopicDTO -> TopicDTO` |
| `POST /api/catalog/exercise-types` | Crear tipo de ejercicio bajo tema | `CreateExerciseTypeDTO -> ExerciseTypeDTO` |
| `POST /api/students/{id}/sessions` | Registrar sesión + intentos | `RecordSessionDTO -> SessionDTO` |
| `GET /api/students/{id}/sessions` | Historial cronológico (memoria) | `SessionDTO[]` |
| `GET /api/students/{id}/diagnostic` | Ejecutar diagnóstico pedagógico | `StudentDiagnosticDTO` |

---

## 4. Diseño del Motor Analítico Determinista (Zero LLM)

1. **Decaimiento temporal (Recencia):**
   Cada intento recibe peso temporal exponencial $w_t = e^{-\lambda \cdot \Delta d}$ (donde $\Delta d$ son los días transcurridos desde la sesión hasta `reference_date`), dando mayor peso a errores recientes sin olvidar el historial.
2. **Tasa ponderada de fallo:**
   $\text{severity}(\text{SUCCESS})=0.0$, $\text{PARTIAL}=0.5$, $\text{FAILURE}=1.0$.  
   $\text{weighted\_failure\_rate} = \frac{\sum (w_t \cdot \text{severity})}{\sum w_t}$.
3. **Urgencia de examen (`ExamGoal`):**
   Si existe un examen próximo ($\le 14$ días) en una asignatura, se aplica un multiplicador/bono de urgencia inversamente proporcional a `days_remaining`, elevando su `priority_score` y generando un `ExamAlert`.
4. **Causa de error dominante:**
   Moda ponderada por recencia de `ErrorCause` en los intentos con fallo/parcial de cada `ExerciseType`.
5. **Tendencia evolutiva (`LearningTrend`):**
   Comparación entre ventana reciente (últimos $N$ intentos o últimas 2 semanas) frente a ventana previa; mejora o empeoramiento superior a un umbral $\delta$ clasifica en `IMPROVING`, `REGRESSING` o `STAGNANT` (si hay $< 4$ intentos, `INSUFFICIENT_DATA`).
6. **Puente a ML Clásico (`FeatureExtractor` + `SklearnPedagogicalAnalyzer`):**
   `FeatureExtractor` transforma sesiones y catálogo en vectores numéricos tabulares homogéneos (tasa de fallo por `ExerciseType`, distribución de `ErrorCause`, días hasta examen, pendiente de mejora) para entrenar modelos locales (`DecisionTreeClassifier` / `LogisticRegression`) sin cambiar el contrato de `PedagogicalAnalyzerPort`.

---

## 5. Estrategia de Testing y Protocolo Micro-TDD

En cada fila de la matriz inferior se aplicará **estrictamente** el ciclo:
1. Crear **stub tipado** que lance `NotImplementedError("Not implemented")` (o `throw new Error("Not implemented")` en TS) + test unitario/integración que defina el comportamiento esperado.
2. Ejecutar test runner (`pytest` / `vitest`) y verificar fallo **RED** por aserción/stub.
3. Escribir la implementación mínima para pasar a **GREEN**.
4. Ejecutar test runner y verificar paso completo; refactorizar eliminando duplicación.
5. **Frontera UI:** En React (`@testing-library/react`), testear exclusivamente conducta visible, flujos de usuario y accesibilidad (`getByRole`, `getByLabelText`, `findByText`), **nunca** clases CSS/Tailwind ni detalles internos; aislar la API con mocks tipados.

---

## 6. Matriz Secuencial de Micro-TDD

### Bloque 0: Inicialización de Entorno
- [x] **T0.1** Inicializar `backend/` (`pyproject.toml` con `fastapi`, `uvicorn`, `pytest`, `mypy`, `scikit-learn` opcional/extra) y verificar `pytest` ejecutándose en vacío.
- [x] **T0.2** Inicializar `frontend/` (Vite + React + TypeScript + `vitest` + `@testing-library/react` + `@testing-library/user-event`) y verificar runner de tests.

### Bloque 1: Dominio OOP Puro (`backend/src/tutoring/domain/`)
- [x] **T1.1** Value Objects y Enums (`AttemptOutcome`, `ErrorCause`, `ExerciseAttempt` con validación de invariantes: fallo/acierto coherente, pesos de severidad).
- [x] **T1.2** Entidades de Catálogo Taxonómico (`Subject`, `Topic`, `ExerciseType` y `AcademicCatalogSnapshot` con resolución jerárquica y validación de nombres).
- [x] **T1.3** Entidad Rica `Student` y `ExamGoal` (validación de fechas, cálculo de `days_remaining`, filtro de exámenes próximos).
- [x] **T1.4** Entidad Rica `TutoringSession` (registro de intentos, cálculo de `failure_rate()`, invariantes de duración y notas).

### Bloque 2: Motor Analítico Determinista & Feature Extractor (`domain/analytics/`)
- [x] **T2.1** `HeuristicPedagogicalAnalyzer` — caso sin sesiones (`INSUFFICIENT_DATA`, scores vacíos/neutros, sin errores).
- [x] **T2.2** Cálculo de tasa de fallo ponderada por recencia (errores recientes pesan más que errores antiguos).
- [x] **T2.3** Ranking de `SubjectPriority` con factor de urgencia por `ExamGoal` próximo y generación de `ExamAlert` + `reasons` explicables.
- [x] **T2.4** Detección de `WeakExerciseType` y `dominant_error_cause` ponderada por recencia.
- [x] **T2.5** Cálculo de `LearningTrend` (`IMPROVING`, `STAGNANT`, `REGRESSING`) comparando ventanas temporales.
- [x] **T2.6** `FeatureExtractor` determinista (convierte memoria del alumno en vector numérico limpio para ML clásico).

### Bloque 3: Capa de Aplicación (`application/use_cases/`)
- [x] **T3.1** In-Memory Repositories (`InMemoryStudentRepo`, `InMemoryCatalogRepo`, `InMemorySessionRepo`) para tests rápidos de aplicación.
- [x] **T3.2** Caso de uso `ManageCatalog` (crear asignaturas, temas y tipos de ejercicio validando existencia de padres).
- [x] **T3.3** Caso de uso `ManageStudents` (alta, ficha detalle, añadir `ExamGoal` validando que la asignatura exista en el catálogo).
- [x] **T3.4** Caso de uso `RecordTutoringSession` (registrar sesión validando que alumno y todos los `exercise_type_id` existan).
- [x] **T3.5** Caso de uso `GenerateStudentDiagnostic` (orquesta repositorios + `PedagogicalAnalyzerPort`).

### Bloque 4: Infraestructura SQLite y Adaptador ML (`infrastructure/`)
- [x] **T4.1** Esquema SQLite y `SqliteCatalogRepository` (tests de integración contra SQLite en memoria/temporal).
- [x] **T4.2** `SqliteStudentRepository` (persistencia y reconstrucción completa de `Student` + `ExamGoal`).
- [x] **T4.3** `SqliteSessionRepository` (persistencia transaccional de `TutoringSession` + `ExerciseAttempt`).
- [x] **T4.4** `SklearnPedagogicalAnalyzer` (adaptador sobre `PedagogicalAnalyzerPort` entrenable con `FeatureExtractor` y fallback seguro a heurístico cuando el modelo aún no está entrenado).

### Bloque 5: Capa de Presentación API FastAPI (`presentation/api/`)
- [x] **T5.1** Mapeo de `DomainError` a códigos HTTP (`404`, `422`, `409`) y endpoints de `/api/catalog`.
- [x] **T5.2** Endpoints `/api/students` y `/api/students/{id}/exam-goals`.
- [x] **T5.3** Endpoints `/api/students/{id}/sessions` y `/api/students/{id}/diagnostic`.

### Bloque 6: Frontend React + TypeScript (`frontend/src/`)
- [x] **T6.1** `CatalogPage`: visualizar árbol Asignatura/Tema/Tipo y crear nuevos elementos (API mockeada, test de conducta y accesibilidad).
- [x] **T6.2** `StudentsPage` y `StudentDetailPage`: listar/crear alumnos, consultar ficha y añadir objetivos de examen.
- [x] **T6.3** `RecordSessionPage`: flujo rápido tras clase para añadir múltiples `ExerciseAttempt` (con selector de catálogo, resultado `Acierto/Parcial/Fallo` y causa del error).
- [x] **T6.4** `StudentDiagnosticPanel`: mostrar ranking de asignaturas prioritarias, motivos explicables, ejercicios con mayor fallo y alertas de exámenes.
- [x] **T6.5** Verificación E2E local (arranque Backend + Frontend y prueba de flujo completo).

---

> **Checkpoint de Aprobación:** Este plan está detenido en **Fase 3**. No se ha creado ni ejecutado código todavía. Confirma si apruebas este plan (o indica cualquier ajuste) para iniciar la **Fase 4 (Micro-TDD)** comenzando por el Bloque 0 y Bloque 1.
