# ML Automatic & Resource-Bounded Training Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement an automatic, resource-bounded supervised ML training pipeline that learns from real exam grades and exercise attempt outcomes, persists validated models atomically to disk, and hot-reloads predictions without blocking HTTP requests.

**Architecture:** The domain gains `ExamResult` on `ExamGoal` and a deterministic `TrainingDatasetBuilder` that constructs anti-leakage `(X, y)` checkpoints using `FeatureExtractor`. Application use cases emit non-blocking notifications to a `TrainingTriggerPort` implemented by a coalescing `BackgroundTrainingCoordinator` (`ThreadPoolExecutor(max_workers=1)` + debounce timer) that runs a quality-gated `PedagogicalModelTrainer` and atomically persists/swaps `SklearnPedagogicalAnalyzer` artifacts via `ModelArtifactStore`.

**Tech Stack:** Python 3.11+, FastAPI, SQLite (WAL + shared `RLock`), scikit-learn (`RandomForestClassifier`, `DummyClassifier`, `StratifiedKFold`, `cross_val_score`), `joblib`, `pytest`, `pytest-asyncio`, `mypy` (strict).

**Spec:** [2026-11-16-ml-training-pipeline-design.md](file:///C:/Users/Perrotruco/Workspace/Clases/docs/superpowers/specs/2026-11-16-ml-training-pipeline-design.md)

---

## Global Constraints

- **Ground Truth híbrido:** Prioridad ALTA (`target = 1`) si el examen asociado fue suspenso (`score < 5.0` normalizado sobre 10) O si `weighted_failure_rate > 0.40`; en caso contrario NORMAL (`target = 0`).
- **Endpoint de calificaciones:** `POST /api/students/{id}/exam-goals/{goal_id}/result` (registra la nota y marca el objetivo como evaluado).
- **Guardarraíles de recursos (Debounce / Coalescencia):** Retardo por defecto de `5.0` segundos o al acumular una ráfaga pendiente de `10` eventos; múltiples eventos en la ventana se fusionan en un único job.
- **Worker unitario:** `ThreadPoolExecutor(max_workers=1)` y estimadores con `n_jobs=1` para que el impacto de CPU quede acotado a 1 núcleo sin competir con endpoints HTTP.
- **Umbral mínimo y Gating:** Mínimo `20` muestras con validación cruzada estratificada (`cv=3`) superando la línea base (`DummyClassifier`); si falla o faltan datos, conservar modelo previo o fallback heurístico.
- **Persistencia en disco:** `active_analyzer.joblib` y `active_analyzer_meta.json` con escritura atómica, carga perezosa y swap atómico en memoria.
- **Sin dependencias pesadas ni bloqueo HTTP:** Cero Redis, Celery, Kafka o Deep Learning; ninguna petición HTTP espera al entrenamiento.

---

## Review Focus

1. **Dataset con una sola clase o clase minoritaria < `cv_folds`:** Si hay `>= 20` muestras pero todas son `target=0` o solo hay 1-2 muestras de `target=1`, `StratifiedKFold(n_splits=3)` fallaría con `ValueError`; el trainer debe devolver `SKIPPED_SINGLE_CLASS` sin crashear ni sobreescribir el modelo activo. *(Cubierto en Task 6)*
2. **`ExamGoal` ya evaluado generando alertas falsas de examen próximo:** Una vez registrado `ExamResult`, `ExamGoal.is_upcoming(...)` debe devolver `False` aunque `exam_date` sea hoy o futuro, evitando alertas obsoletas en `HeuristicPedagogicalAnalyzer` y `FeatureExtractor`. *(Cubierto en Task 1)*
3. **Contención SQLite entre hilo HTTP y worker en segundo plano:** Lecturas del dataset en `ThreadPoolExecutor` compartiendo conexión `:memory:` o fichero con FastAPI provocarían `sqlite3.OperationalError: cannot start a transaction within a transaction`; todos los repositorios SQLite y la extracción de snapshot deben sincronizarse con un `threading.RLock` liberado antes del cómputo ML. *(Cubierto en Task 4)*
4. **Artefacto `.joblib` corrupto o desalineado tras cambio de features:** Si el archivo en disco está corrupto o `active_analyzer_meta.json` declara `feature_names` distintos de `FeatureExtractor.FEATURE_NAMES`, `ModelArtifactStore.load()` debe descartarlo con seguridad y mantener el fallback heurístico. *(Cubierto en Task 5)*
5. **Sesiones sin intentos o eventos duplicados sin datos nuevos:** Registrar una sesión con `attempts=()` o re-notificar sin cambios reales en el dataset no debe disparar `cross_val_score` + `fit()`, cortocircuitando mediante `attempts` no vacíos y `dataset_hash` en `SKIPPED_UNCHANGED`. *(Cubierto en Tasks 3, 6 y 8)*

---

## Matriz Secuencial de Micro-TDD

| Orden | Tarea | Módulo / Capa | Entregable Verificable | Comando de Verificación |
| :--- | :--- | :--- | :--- | :--- |
| 1 | `ExamResult` y `Student.record_exam_result` | `domain/` | Value object validado, `is_upcoming` excluye evaluados | `.venv\Scripts\pytest.exe backend\tests\unit\domain\test_student_entity.py -v` |
| 2 | `TrainingDatasetBuilder` anti-leakage | `domain/analytics/` | Construcción determinista `(X, y, hash)` con regla híbrida | `.venv\Scripts\pytest.exe backend\tests\unit\domain\test_dataset_builder.py -v` |
| 3 | Puertos, DTOs y casos de uso con trigger | `domain/ports/` + `application/` | `TrainingTriggerPort`, `record_exam_result` y trigger en `record_session` | `.venv\Scripts\pytest.exe backend\tests\unit\application -v` |
| 4 | Tabla `exam_results` y bloqueo SQLite | `infrastructure/persistence/` | Persistencia `ExamResult` y concurrencia segura con `RLock` | `.venv\Scripts\pytest.exe backend\tests\integration\test_sqlite_student_repo.py -v` |
| 5 | `ModelArtifactStore` y `SklearnPedagogicalAnalyzer` | `infrastructure/ml/` | Guardado/carga atómica `joblib`, lazy load y hot-swap seguro | `.venv\Scripts\pytest.exe backend\tests\integration\test_sklearn_analyzer.py -v` |
| 6 | `PedagogicalModelTrainer` con Quality Gating | `infrastructure/ml/` | Validación CV vs baseline, `n_jobs=1`, manejo de clases únicas | `.venv\Scripts\pytest.exe backend\tests\integration\test_ml_trainer.py -v` |
| 7 | `BackgroundTrainingCoordinator` con debounce | `infrastructure/ml/` | Coalescencia 5s / ráfaga 10, `max_workers=1`, `flush`/`shutdown` | `.venv\Scripts\pytest.exe backend\tests\integration\test_background_coordinator.py -v` |
| 8 | API FastAPI, `lifespan` y prueba E2E | `presentation/api/` | Endpoint `POST .../result`, cableado ML y auto-entrenamiento E2E | `.venv\Scripts\pytest.exe backend -v && .venv\Scripts\mypy.exe backend\src` |

---

## Contratos de Interfaz Principales

```python
# domain/value_objects/exam_goal.py
@dataclass(frozen=True)
class ExamResult:
    score: float
    max_score: float = 10.0
    recorded_at: datetime
    notes: str = ""
    @property
    def normalized_score_10(self) -> float: ...
    @property
    def is_passing(self) -> bool: ...  # normalized_score_10 >= 5.0

# domain/ports/ml_training.py
class TrainingTriggerPort(Protocol):
    def notify_new_data(self) -> None: ...

# domain/analytics/dataset_builder.py
@dataclass(frozen=True)
class TrainingDataset:
    features: tuple[tuple[float, ...], ...]
    labels: tuple[int, ...]
    feature_names: tuple[str, ...]
    dataset_hash: str

# infrastructure/ml/trainer.py
class TrainingStatus(str, Enum):
    TRAINED = "TRAINED"
    SKIPPED_UNCHANGED = "SKIPPED_UNCHANGED"
    SKIPPED_INSUFFICIENT_DATA = "SKIPPED_INSUFFICIENT_DATA"
    SKIPPED_SINGLE_CLASS = "SKIPPED_SINGLE_CLASS"
    REJECTED_QUALITY = "REJECTED_QUALITY"
    FAILED = "FAILED"
```

---

### Task 1: Domain `ExamResult` Value Object & `Student.record_exam_result`

**Files:**
- Modify: `backend/src/tutoring/domain/value_objects/exam_goal.py:1-34`
- Modify: `backend/src/tutoring/domain/value_objects/__init__.py:1-19`
- Modify: `backend/src/tutoring/domain/entities/student.py:51-95`
- Test: `backend/tests/unit/domain/test_student_entity.py`

**Interfaces:**
- Consumes: `ValidationError`, `DuplicateEntityError`, `EntityNotFoundError` from `tutoring.domain.exceptions`
- Produces:
  - `ExamResult(score: float, recorded_at: datetime, max_score: float = 10.0, notes: str = "")` with `normalized_score_10: float` and `is_passing: bool`
  - `ExamGoal(..., result: ExamResult | None = None)` with `with_result(result: ExamResult) -> ExamGoal` and `is_upcoming(...) -> bool`
  - `Student.record_exam_result(goal_id: UUID, result: ExamResult) -> ExamGoal`

- [ ] **Step 1: Write failing tests for `ExamResult`, `ExamGoal.with_result`, evaluated `is_upcoming`, and `Student.record_exam_result`**

Append to `backend/tests/unit/domain/test_student_entity.py`:

```python
from datetime import datetime, timezone
from tutoring.domain.exceptions import EntityNotFoundError
from tutoring.domain.value_objects.exam_goal import ExamResult


def test_exam_result_validates_bounds_and_normalizes_score() -> None:
    ts = datetime(2026, 11, 16, 18, 0, tzinfo=timezone.utc)
    passing = ExamResult(score=5.0, max_score=10.0, recorded_at=ts, notes="  Justo  ")
    assert passing.normalized_score_10 == 5.0
    assert passing.is_passing is True
    assert passing.notes == "Justo"

    scaled_fail = ExamResult(score=49.0, max_score=100.0, recorded_at=ts)
    assert scaled_fail.normalized_score_10 == 4.9
    assert scaled_fail.is_passing is False

    for bad_score, bad_max in [(-0.1, 10.0), (10.5, 10.0), (5.0, 0.0), (float("nan"), 10.0)]:
        with pytest.raises(ValidationError):
            ExamResult(score=bad_score, max_score=bad_max, recorded_at=ts)


def test_exam_goal_with_result_is_no_longer_upcoming() -> None:
    today = date(2026, 11, 16)
    goal = ExamGoal(id=uuid4(), subject_id=uuid4(), title="Parcial", exam_date=today)
    assert goal.is_upcoming(today, horizon_days=14) is True

    result = ExamResult(score=7.5, recorded_at=datetime(2026, 11, 16, 18, 0, tzinfo=timezone.utc))
    evaluated = goal.with_result(result)
    assert evaluated.result == result
    assert evaluated.is_upcoming(today, horizon_days=14) is False

    with pytest.raises(DuplicateEntityError):
        evaluated.with_result(result)


def test_student_record_exam_result_lifecycle() -> None:
    today = date(2026, 11, 16)
    student = Student(id=uuid4(), full_name="Sofía", academic_level="2º ESO")
    goal = ExamGoal(id=uuid4(), subject_id=uuid4(), title="Álgebra", exam_date=date(2026, 11, 20))
    student.add_exam_goal(goal, today=today)

    result = ExamResult(score=4.2, recorded_at=datetime(2026, 11, 20, 17, 0, tzinfo=timezone.utc))
    with pytest.raises(EntityNotFoundError):
        student.record_exam_result(uuid4(), result)

    updated = student.record_exam_result(goal.id, result)
    assert updated.result == result
    assert student.exam_goals[0].result == result

    with pytest.raises(DuplicateEntityError):
        student.record_exam_result(goal.id, result)
```

- [ ] **Step 2: Run test to verify RED**

Run: `.venv\Scripts\pytest.exe backend\tests\unit\domain\test_student_entity.py -v`
Expected: FAIL (`ImportError: cannot import name 'ExamResult'`).

- [ ] **Step 3: Implement `ExamResult`, update `ExamGoal` and `Student.record_exam_result`**

- In `backend/src/tutoring/domain/value_objects/exam_goal.py`:
  - Define `@dataclass(frozen=True) class ExamResult` with `score: float`, `recorded_at: datetime`, `max_score: float = 10.0`, `notes: str = ""`. In `__post_init__`, validate `math.isfinite(self.score)`, `math.isfinite(self.max_score)`, `self.max_score > 0.0`, `0.0 <= self.score <= self.max_score`, and strip `notes`.
  - Implement `normalized_score_10` (`round((self.score / self.max_score) * 10.0, 4)`) and `is_passing` (`self.normalized_score_10 >= 5.0`).
  - Add `result: ExamResult | None = None` to `ExamGoal`, update `is_upcoming` to return `False` when `self.result is not None`, and add `with_result(self, result: ExamResult) -> ExamGoal` using `dataclasses.replace` (raising `DuplicateEntityError` if `self.result is not None`).
- Export `ExamResult` in `backend/src/tutoring/domain/value_objects/__init__.py`.
- In `backend/src/tutoring/domain/entities/student.py`:
  - Add `record_exam_result(self, goal_id: UUID, result: ExamResult) -> ExamGoal` searching `self._exam_goals`, raising `EntityNotFoundError` if missing, replacing the element with `goal.with_result(result)`, and returning the updated `ExamGoal`.

- [ ] **Step 4: Run test to verify GREEN**

Run: `.venv\Scripts\pytest.exe backend\tests\unit\domain\test_student_entity.py -v`
Expected: PASS (all tests in `test_student_entity.py`).

- [ ] **Step 5: Commit**

```bash
git add backend/src/tutoring/domain/value_objects/exam_goal.py backend/src/tutoring/domain/value_objects/__init__.py backend/src/tutoring/domain/entities/student.py backend/tests/unit/domain/test_student_entity.py
git commit -m "feat(domain): add ExamResult value object and Student.record_exam_result"
```

---

### Task 2: Domain `TrainingDatasetBuilder` (Hybrid Labeling & Anti-Leakage)

**Files:**
- Create: `backend/src/tutoring/domain/analytics/dataset_builder.py`
- Test: `backend/tests/unit/domain/test_dataset_builder.py`

**Interfaces:**
- Consumes:
  - `FeatureExtractor.extract_subject_features(student, subject_id, sessions, catalog, reference_date) -> FeatureVector`
  - `Student`, `TutoringSession`, `AcademicCatalogSnapshot`, `ExamGoal`, `ExamResult`
- Produces:
  - `TrainingDataset(features: tuple[tuple[float, ...], ...], labels: tuple[int, ...], feature_names: tuple[str, ...], dataset_hash: str)`
  - `TrainingDatasetBuilder(feature_extractor: FeatureExtractor | None = None, failure_threshold: float = 0.40, exam_horizon_days: int = 14, max_samples: int = 5000)`
  - `TrainingDatasetBuilder.build(students: Sequence[Student], sessions_by_student: Mapping[UUID, Sequence[TutoringSession]], catalog: AcademicCatalogSnapshot) -> TrainingDataset`

- [ ] **Step 1: Write failing tests for `TrainingDatasetBuilder`**

Create `backend/tests/unit/domain/test_dataset_builder.py`:

```python
from datetime import date, datetime, timezone
from uuid import uuid4

from tutoring.domain.analytics.dataset_builder import TrainingDatasetBuilder
from tutoring.domain.entities.catalog import AcademicCatalogSnapshot, ExerciseType, Subject, Topic
from tutoring.domain.entities.session import TutoringSession
from tutoring.domain.entities.student import Student
from tutoring.domain.enums import AttemptOutcome, ErrorCause
from tutoring.domain.value_objects.attempt import ExerciseAttempt
from tutoring.domain.value_objects.exam_goal import ExamGoal, ExamResult


def test_dataset_builder_applies_hybrid_labeling_and_prevents_future_leakage() -> None:
    math = Subject(id=uuid4(), name="Matemáticas")
    topic = Topic(id=uuid4(), subject_id=math.id, name="Álgebra")
    ex = ExerciseType(id=uuid4(), topic_id=topic.id, name="Ecuaciones")
    catalog = AcademicCatalogSnapshot(subjects=[math], topics=[topic], exercise_types=[ex])

    exam_date = date(2026, 11, 10)
    failed_goal = ExamGoal(
        id=uuid4(),
        subject_id=math.id,
        title="Parcial 1",
        exam_date=exam_date,
        result=ExamResult(score=4.5, recorded_at=datetime(2026, 11, 11, 10, 0, tzinfo=timezone.utc)),
    )
    student = Student(id=uuid4(), full_name="Hugo", academic_level="4º ESO", exam_goals=[failed_goal])

    # Pre-exam session has LOW failure (0.0) -> still labeled 1 because exam failed (< 5.0)
    s_before = TutoringSession(
        id=uuid4(),
        student_id=student.id,
        occurred_at=datetime(2026, 11, 5, 17, 0, tzinfo=timezone.utc),
        duration_minutes=60,
        attempts=[ExerciseAttempt(ex.id, AttemptOutcome.SUCCESS)],
    )
    # Post-exam session on Nov 15 with HIGH failure (1.0) must NOT leak into Nov 10 checkpoint
    s_after = TutoringSession(
        id=uuid4(),
        student_id=student.id,
        occurred_at=datetime(2026, 11, 15, 17, 0, tzinfo=timezone.utc),
        duration_minutes=60,
        attempts=[ExerciseAttempt(ex.id, AttemptOutcome.FAILURE, ErrorCause.CONCEPT)],
    )

    builder = TrainingDatasetBuilder()
    dataset = builder.build([student], {student.id: [s_before, s_after]}, catalog)

    # Checkpoints: Nov 5 (session before failing exam within 14d -> 1), Nov 10 (exam -> 1, sessions_count=1.0), Nov 15 (session failure>0.4 -> 1)
    assert len(dataset.features) == 3
    assert dataset.labels == (1, 1, 1)
    sessions_count_idx = dataset.feature_names.index("sessions_count")
    # Nov 10 exam checkpoint must see only 1 session (s_before), not s_after
    assert dataset.features[1][sessions_count_idx] == 1.0


def test_dataset_builder_labels_normal_when_passing_and_low_failure_and_ignores_empty_sessions() -> None:
    math = Subject(id=uuid4(), name="Matemáticas")
    topic = Topic(id=uuid4(), subject_id=math.id, name="Álgebra")
    ex = ExerciseType(id=uuid4(), topic_id=topic.id, name="Ecuaciones")
    catalog = AcademicCatalogSnapshot(subjects=[math], topics=[topic], exercise_types=[ex])

    passed_goal = ExamGoal(
        id=uuid4(),
        subject_id=math.id,
        title="Parcial 1",
        exam_date=date(2026, 11, 10),
        result=ExamResult(score=8.0, recorded_at=datetime(2026, 11, 10, 19, 0, tzinfo=timezone.utc)),
    )
    student = Student(id=uuid4(), full_name="Alba", academic_level="1º Bach", exam_goals=[passed_goal])

    s_same_day = TutoringSession(
        id=uuid4(),
        student_id=student.id,
        occurred_at=datetime(2026, 11, 10, 10, 0, tzinfo=timezone.utc),
        duration_minutes=60,
        attempts=[ExerciseAttempt(ex.id, AttemptOutcome.SUCCESS)],
    )
    s_empty = TutoringSession(
        id=uuid4(),
        student_id=student.id,
        occurred_at=datetime(2026, 11, 12, 10, 0, tzinfo=timezone.utc),
        duration_minutes=30,
        attempts=[],
    )

    builder = TrainingDatasetBuilder()
    ds_without_empty = builder.build([student], {student.id: [s_same_day]}, catalog)
    ds_with_empty = builder.build([student], {student.id: [s_same_day, s_empty]}, catalog)

    # Deduplicated on Nov 10 -> 1 sample, labeled 0; empty session produces no change
    assert len(ds_without_empty.features) == 1
    assert ds_without_empty.labels == (0,)
    assert ds_without_empty.dataset_hash == ds_with_empty.dataset_hash


def test_dataset_builder_respects_max_samples_cap() -> None:
    math = Subject(id=uuid4(), name="Matemáticas")
    topic = Topic(id=uuid4(), subject_id=math.id, name="Aritmética")
    ex = ExerciseType(id=uuid4(), topic_id=topic.id, name="Sumas")
    catalog = AcademicCatalogSnapshot(subjects=[math], topics=[topic], exercise_types=[ex])
    student = Student(id=uuid4(), full_name="Leo", academic_level="1º ESO")
    sessions = [
        TutoringSession(
            id=uuid4(),
            student_id=student.id,
            occurred_at=datetime(2026, 11, day, 17, 0, tzinfo=timezone.utc),
            duration_minutes=45,
            attempts=[ExerciseAttempt(ex.id, AttemptOutcome.SUCCESS)],
        )
        for day in range(1, 11)
    ]

    dataset = TrainingDatasetBuilder(max_samples=4).build([student], {student.id: sessions}, catalog)
    assert len(dataset.features) == 4
```

- [ ] **Step 2: Run test to verify RED**

Run: `.venv\Scripts\pytest.exe backend\tests\unit\domain\test_dataset_builder.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'tutoring.domain.analytics.dataset_builder'`).

- [ ] **Step 3: Implement `TrainingDataset` and `TrainingDatasetBuilder` in `backend/src/tutoring/domain/analytics/dataset_builder.py`**

Implement checkpoint generation sorted chronologically by `(ref_date, str(student.id), str(subject_id))`:
1. Build pre-checkpoint `Student` view with `dataclasses.replace(g, result=None)` for goals where `g.exam_date >= ref_date` so train-time `upcoming_exams` matches serve-time feature vectors.
2. Emit evaluated `ExamGoal` checkpoints (`goal.result is not None` and subject exists in `catalog`): filter `sessions <= goal.exam_date`, extract `FeatureVector`, label `1` if `not goal.result.is_passing or weighted_failure_rate > failure_threshold` else `0`.
3. Emit distinct `(student.id, subject_id, session_date)` checkpoints from sessions with attempts (skipping keys already emitted as exam checkpoints): label `1` if `weighted_failure_rate > failure_threshold` or an evaluated goal in `subject_id` within `(ref_date, ref_date + exam_horizon_days]` has `not result.is_passing`, else `0`.
4. Retain the most recent `max_samples` entries and hash `(feature_names, features, labels)` via `hashlib.sha256` (rounded floats `round(v, 8)` for deterministic JSON serialization).

- [ ] **Step 4: Run test to verify GREEN**

Run: `.venv\Scripts\pytest.exe backend\tests\unit\domain\test_dataset_builder.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/src/tutoring/domain/analytics/dataset_builder.py backend/tests/unit/domain/test_dataset_builder.py
git commit -m "feat(domain): add anti-leakage TrainingDatasetBuilder with hybrid labeling"
```

---

### Task 3: Application Ports, DTOs & Use Case Triggers (`ExamResult` + `TrainingTriggerPort`)

**Files:**
- Create: `backend/src/tutoring/domain/ports/ml_training.py`
- Modify: `backend/src/tutoring/domain/ports/__init__.py:1-16`
- Modify: `backend/src/tutoring/application/dtos.py:83-115`
- Modify: `backend/src/tutoring/application/fakes.py:1-94`
- Modify: `backend/src/tutoring/application/use_cases/manage_students.py:1-107`
- Modify: `backend/src/tutoring/application/use_cases/record_session.py:1-60`
- Test: `backend/tests/unit/application/test_manage_students.py`
- Test: `backend/tests/unit/application/test_record_session.py`

**Interfaces:**
- Consumes: `ExamResult` (Task 1), `Student.record_exam_result` (Task 1)
- Produces:
  - `TrainingTriggerPort.notify_new_data() -> None`
  - `FakeTrainingTrigger` with `.trigger_count: int`
  - `RecordExamResultDTO(score: float, recorded_at: datetime, max_score: float = 10.0, notes: str = "")`
  - `ExamResultDTO(score: float, max_score: float, normalized_score_10: float, is_passing: bool, recorded_at: datetime, notes: str)`
  - `ExamGoalDTO(..., result: ExamResultDTO | None = None)`
  - `ManageStudentsUseCase.record_exam_result(student_id: UUID, goal_id: UUID, dto: RecordExamResultDTO) -> ExamGoalDTO`

- [ ] **Step 1: Write failing unit tests for `ManageStudentsUseCase.record_exam_result` and `RecordSessionUseCase` training trigger**

Append to `backend/tests/unit/application/test_manage_students.py`:

```python
from datetime import datetime, timezone
from tutoring.application.dtos import RecordExamResultDTO
from tutoring.application.fakes import FakeTrainingTrigger
from tutoring.domain.exceptions import DuplicateEntityError


def test_record_exam_result_persists_grade_and_notifies_trigger() -> None:
    student_repo = InMemoryStudentRepository()
    catalog_repo = InMemoryCatalogRepository()
    trigger = FakeTrainingTrigger()
    use_case = ManageStudentsUseCase(
        student_repo=student_repo, catalog_repo=catalog_repo, training_trigger=trigger
    )
    subject = Subject(id=uuid4(), name="Física")
    catalog_repo.save_subject(subject)
    student = use_case.create_student(CreateStudentDTO(full_name="Elena", academic_level="2º Bach"))
    goal = use_case.add_exam_goal(
        student.id,
        CreateExamGoalDTO(subject_id=subject.id, title="Óptica", exam_date=date(2026, 11, 25)),
        today=date(2026, 11, 16),
    )

    updated = use_case.record_exam_result(
        student_id=student.id,
        goal_id=goal.id,
        dto=RecordExamResultDTO(
            score=4.0,
            max_score=10.0,
            recorded_at=datetime(2026, 11, 25, 18, 0, tzinfo=timezone.utc),
            notes="Repasar lentes",
        ),
    )
    assert updated.result is not None
    assert updated.result.score == 4.0
    assert updated.result.is_passing is False
    assert trigger.trigger_count == 1

    with pytest.raises(DuplicateEntityError):
        use_case.record_exam_result(
            student.id,
            goal.id,
            RecordExamResultDTO(score=6.0, recorded_at=datetime(2026, 11, 25, 19, 0, tzinfo=timezone.utc)),
        )
    assert trigger.trigger_count == 1
```

Append to `backend/tests/unit/application/test_record_session.py`:

```python
from tutoring.application.fakes import FakeTrainingTrigger


def test_record_session_notifies_trigger_only_when_attempts_present() -> None:
    student_repo = InMemoryStudentRepository()
    catalog_repo = InMemoryCatalogRepository()
    session_repo = InMemorySessionRepository()
    trigger = FakeTrainingTrigger()
    use_case = RecordSessionUseCase(
        student_repo=student_repo,
        catalog_repo=catalog_repo,
        session_repo=session_repo,
        training_trigger=trigger,
    )
    student = Student(id=uuid4(), full_name="Hugo", academic_level="3º ESO")
    student_repo.save(student)
    subject = Subject(id=uuid4(), name="Lengua")
    topic = Topic(id=uuid4(), subject_id=subject.id, name="Sintaxis")
    ex_type = ExerciseType(id=uuid4(), topic_id=topic.id, name="Oraciones")
    catalog_repo.save_subject(subject)
    catalog_repo.save_topic(topic)
    catalog_repo.save_exercise_type(ex_type)

    # Empty attempts -> does not trigger retraining
    use_case.execute(
        student.id,
        RecordSessionDTO(
            occurred_at=datetime(2026, 11, 16, 17, 0, tzinfo=timezone.utc),
            duration_minutes=30,
            attempts=(),
        ),
    )
    assert trigger.trigger_count == 0

    # Session with attempts -> notifies trigger
    use_case.execute(
        student.id,
        RecordSessionDTO(
            occurred_at=datetime(2026, 11, 16, 18, 0, tzinfo=timezone.utc),
            duration_minutes=60,
            attempts=(ExerciseAttemptInputDTO(ex_type.id, AttemptOutcome.SUCCESS),),
        ),
    )
    assert trigger.trigger_count == 1
```

- [ ] **Step 2: Run tests to verify RED**

Run: `.venv\Scripts\pytest.exe backend\tests\unit\application -v`
Expected: FAIL (`ImportError` / unexpected keyword argument `training_trigger`).

- [ ] **Step 3: Implement `TrainingTriggerPort`, DTOs, `FakeTrainingTrigger`, and use case updates**

- Create `backend/src/tutoring/domain/ports/ml_training.py` defining `TrainingTriggerPort(Protocol)` with `def notify_new_data(self) -> None: ...`, and export it in `domain/ports/__init__.py`.
- Add `RecordExamResultDTO`, `ExamResultDTO`, and `result: ExamResultDTO | None = None` on `ExamGoalDTO` in `backend/src/tutoring/application/dtos.py`.
- Add `FakeTrainingTrigger(TrainingTriggerPort)` in `backend/src/tutoring/application/fakes.py`.
- Update `ManageStudentsUseCase` (`training_trigger: TrainingTriggerPort | None = None`) with `record_exam_result(...)` and `_to_exam_goal_dto(...)`.
- Update `RecordSessionUseCase` (`training_trigger: TrainingTriggerPort | None = None`) to invoke `self._training_trigger.notify_new_data()` inside `if session.attempts and self._training_trigger is not None:`.

- [ ] **Step 4: Run tests to verify GREEN**

Run: `.venv\Scripts\pytest.exe backend\tests\unit\application -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/src/tutoring/domain/ports/ml_training.py backend/src/tutoring/domain/ports/__init__.py backend/src/tutoring/application/dtos.py backend/src/tutoring/application/fakes.py backend/src/tutoring/application/use_cases/manage_students.py backend/src/tutoring/application/use_cases/record_session.py backend/tests/unit/application/test_manage_students.py backend/tests/unit/application/test_record_session.py
git commit -m "feat(application): add ExamResult DTOs, record_exam_result use case, and TrainingTriggerPort"
```

---

### Task 4: SQLite Persistence for `exam_results` & Thread-Safe Repository Locking

**Files:**
- Modify: `backend/src/tutoring/infrastructure/persistence/sqlite_db.py:52-69`
- Modify: `backend/src/tutoring/infrastructure/persistence/sqlite_student_repo.py:13-120`
- Modify: `backend/src/tutoring/infrastructure/persistence/sqlite_session_repo.py:14-116`
- Modify: `backend/src/tutoring/infrastructure/persistence/sqlite_catalog_repo.py:15-149`
- Test: `backend/tests/integration/test_sqlite_student_repo.py`

**Interfaces:**
- Consumes: `ExamResult`, `ExamGoal` (Task 1)
- Produces:
  - `exam_results` table in `SCHEMA_SQL`
  - `SqliteStudentRepository(conn: sqlite3.Connection, lock: threading.RLock | None = None)`
  - `SqliteSessionRepository(conn: sqlite3.Connection, lock: threading.RLock | None = None)`
  - `SqliteCatalogRepository(conn: sqlite3.Connection, lock: threading.RLock | None = None)`

- [ ] **Step 1: Write failing integration tests for `ExamResult` SQLite persistence and concurrent thread safety**

Append to `backend/tests/integration/test_sqlite_student_repo.py`:

```python
import threading
from datetime import datetime, timezone
from tutoring.domain.value_objects.exam_goal import ExamResult


def test_sqlite_persists_exam_goal_result_roundtrip() -> None:
    conn = init_sqlite_db(":memory:")
    catalog_repo = SqliteCatalogRepository(conn)
    student_repo = SqliteStudentRepository(conn)

    subject = Subject(id=uuid4(), name="Matemáticas")
    catalog_repo.save_subject(subject)
    student = Student(id=uuid4(), full_name="Nora", academic_level="4º ESO")
    goal = ExamGoal(id=uuid4(), subject_id=subject.id, title="Funciones", exam_date=date(2026, 11, 20))
    student.add_exam_goal(goal, today=date(2026, 11, 16))
    result = ExamResult(
        score=7.25,
        max_score=10.0,
        recorded_at=datetime(2026, 11, 20, 18, 0, tzinfo=timezone.utc),
        notes="Muy bien en gráficas",
    )
    student.record_exam_result(goal.id, result)
    student_repo.save(student)

    loaded = student_repo.get_by_id(student.id)
    assert loaded is not None
    assert loaded.exam_goals[0].result == result


def test_sqlite_repositories_safe_under_concurrent_thread_access() -> None:
    conn = init_sqlite_db(":memory:")
    db_lock = threading.RLock()
    catalog_repo = SqliteCatalogRepository(conn, lock=db_lock)
    student_repo = SqliteStudentRepository(conn, lock=db_lock)

    subject = Subject(id=uuid4(), name="Física")
    catalog_repo.save_subject(subject)
    errors: list[Exception] = []

    def writer() -> None:
        try:
            for i in range(40):
                s = Student(id=uuid4(), full_name=f"Alumno {i}", academic_level="1º Bach")
                student_repo.save(s)
        except Exception as exc:  # pragma: no cover
            errors.append(exc)

    def reader() -> None:
        try:
            for _ in range(40):
                student_repo.list_all()
                catalog_repo.get_snapshot()
        except Exception as exc:  # pragma: no cover
            errors.append(exc)

    t1 = threading.Thread(target=writer)
    t2 = threading.Thread(target=reader)
    t1.start()
    t2.start()
    t1.join(timeout=5)
    t2.join(timeout=5)
    assert errors == []
    assert len(student_repo.list_all()) == 40
```

- [ ] **Step 2: Run test to verify RED**

Run: `.venv\Scripts\pytest.exe backend\tests\integration\test_sqlite_student_repo.py -v`
Expected: FAIL (`AssertionError: assert None == ExamResult(...)` and `TypeError: unexpected keyword argument 'lock'`).

- [ ] **Step 3: Add `exam_results` table, `ExamResult` SQLite mapping, WAL pragma, and optional `RLock` to all 3 SQLite repos**

- In `sqlite_db.py`: add `CREATE TABLE IF NOT EXISTS exam_results (goal_id TEXT PRIMARY KEY REFERENCES exam_goals(id) ON DELETE CASCADE, score REAL NOT NULL, max_score REAL NOT NULL, recorded_at TEXT NOT NULL, notes TEXT NOT NULL DEFAULT '');`. When `str(db_path) != ":memory:"`, run `PRAGMA journal_mode = WAL;` and `PRAGMA busy_timeout = 5000;`.
- In `sqlite_student_repo.py`, `sqlite_session_repo.py`, `sqlite_catalog_repo.py`: accept `lock: threading.RLock | None = None`, wrap every `with self._conn:` and read query with `self._lock if self._lock is not None else contextlib.nullcontext()`.
- In `sqlite_student_repo.py`: inside `save()` insert `exam_results` for goals with `result is not None`; inside `_hydrate_student()` `LEFT JOIN exam_results` on `exam_goals.id = exam_results.goal_id` to reconstruct `ExamResult` when `score IS NOT NULL`.

- [ ] **Step 4: Run test to verify GREEN**

Run: `.venv\Scripts\pytest.exe backend\tests\integration\test_sqlite_student_repo.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/src/tutoring/infrastructure/persistence/sqlite_db.py backend/src/tutoring/infrastructure/persistence/sqlite_student_repo.py backend/src/tutoring/infrastructure/persistence/sqlite_session_repo.py backend/src/tutoring/infrastructure/persistence/sqlite_catalog_repo.py backend/tests/integration/test_sqlite_student_repo.py
git commit -m "feat(persistence): persist ExamResult in SQLite and add thread-safe RLock support"
```

---

### Task 5: Atomic `ModelArtifactStore` & Lazy/Thread-Safe `SklearnPedagogicalAnalyzer`

**Files:**
- Modify: `backend/pyproject.toml:13-17`
- Create: `backend/src/tutoring/infrastructure/ml/model_store.py`
- Modify: `backend/src/tutoring/infrastructure/ml/sklearn_analyzer.py:1-102`
- Test: `backend/tests/integration/test_sklearn_analyzer.py`

**Interfaces:**
- Consumes: `FeatureExtractor.FEATURE_NAMES`
- Produces:
  - `ModelMetadata(version: int, trained_at: datetime, analyzer_name: str, sample_count: int, positive_count: int, negative_count: int, cv_f1_macro: float, baseline_f1_macro: float, dataset_hash: str, feature_names: tuple[str, ...])`
  - `ModelArtifactStore(model_dir: str | Path)` with `.save(model: Any, metadata: ModelMetadata) -> ModelMetadata`, `.load() -> tuple[Any, ModelMetadata] | None`, `.load_metadata() -> ModelMetadata | None`
  - `SklearnPedagogicalAnalyzer(classifier=None, feature_extractor=None, fallback_analyzer=None, model_store: ModelArtifactStore | None = None)` with `.update_model(classifier: Any, metadata: ModelMetadata | None = None) -> None` and `.metadata -> ModelMetadata | None`

- [ ] **Step 1: Write failing tests for atomic persistence, corruption/schema fallback, lazy loading, and thread-safe model swap**

Append to `backend/tests/integration/test_sklearn_analyzer.py`:

```python
import json
from pathlib import Path
from tutoring.domain.analytics.feature_extractor import FeatureExtractor
from tutoring.infrastructure.ml.model_store import ModelArtifactStore, ModelMetadata


def test_model_store_atomic_roundtrip_and_lazy_load(tmp_path: Path) -> None:
    store = ModelArtifactStore(tmp_path)
    clf = DecisionTreeClassifier(random_state=42)
    x_train = [[1.0] * 13, [0.0] * 13]
    clf.fit(x_train, [1, 0])
    meta = ModelMetadata(
        version=1,
        trained_at=datetime(2026, 11, 16, 18, 0, tzinfo=timezone.utc),
        analyzer_name="SklearnPedagogicalAnalyzerV1",
        sample_count=20,
        positive_count=10,
        negative_count=10,
        cv_f1_macro=0.85,
        baseline_f1_macro=0.45,
        dataset_hash="abc123",
        feature_names=FeatureExtractor.FEATURE_NAMES,
    )
    store.save(clf, meta)
    assert (tmp_path / "active_analyzer.joblib").exists()
    assert (tmp_path / "active_analyzer_meta.json").exists()

    # Lazy-loads persisted model on demand
    reloaded_analyzer = SklearnPedagogicalAnalyzer(model_store=store)
    assert reloaded_analyzer.is_trained is True
    assert reloaded_analyzer.metadata == meta


def test_model_store_rejects_corrupted_or_mismatched_schema_and_falls_back(tmp_path: Path) -> None:
    store = ModelArtifactStore(tmp_path)
    (tmp_path / "active_analyzer.joblib").write_bytes(b"corrupt-bytes")
    (tmp_path / "active_analyzer_meta.json").write_text('{"bad": "json"}', encoding="utf-8")
    assert store.load() is None

    # Valid joblib but mismatched feature_names -> rejected
    clf = DecisionTreeClassifier(random_state=42).fit([[0.0] * 13, [1.0] * 13], [0, 1])
    bad_meta = ModelMetadata(
        version=1,
        trained_at=datetime(2026, 11, 16, 18, 0, tzinfo=timezone.utc),
        analyzer_name="SklearnPedagogicalAnalyzerV1",
        sample_count=2,
        positive_count=1,
        negative_count=1,
        cv_f1_macro=0.8,
        baseline_f1_macro=0.5,
        dataset_hash="h",
        feature_names=("legacy_only",),
    )
    store.save(clf, bad_meta)
    assert store.load() is None

    analyzer = SklearnPedagogicalAnalyzer(model_store=store)
    assert analyzer.is_trained is False
```

- [ ] **Step 2: Run test to verify RED**

Run: `.venv\Scripts\pytest.exe backend\tests\integration\test_sklearn_analyzer.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'tutoring.infrastructure.ml.model_store'`).

- [ ] **Step 3: Implement `ModelArtifactStore`, update `pyproject.toml`, and update `SklearnPedagogicalAnalyzer`**

- Add `"joblib>=1.3.0",` to `[project.optional-dependencies].ml` in `backend/pyproject.toml`.
- Create `backend/src/tutoring/infrastructure/ml/model_store.py`:
  - `ModelMetadata` dataclass with `to_dict()` / `from_dict()`.
  - `ModelArtifactStore`: atomic writes using `tempfile` in `model_dir` + `os.replace` for both `active_analyzer.joblib` (`joblib.dump`) and `active_analyzer_meta.json`. In `load()`, verify both files exist, validate `tuple(meta.feature_names) == FeatureExtractor.FEATURE_NAMES`, and catch `(OSError, ValueError, TypeError, KeyError)` / `Exception` on corrupt joblib to log a warning and return `None`.
- Update `backend/src/tutoring/infrastructure/ml/sklearn_analyzer.py`:
  - Add `model_store: ModelArtifactStore | None = None`, `self._lock = threading.RLock()`, `self._metadata: ModelMetadata | None = None`, `self._store_checked = False`.
  - Add `_ensure_loaded()` (loads once from `self._model_store` if `self._classifier is None` and not checked).
  - Add `update_model(self, classifier: Any, metadata: ModelMetadata | None = None) -> None` and `@property def metadata(self) -> ModelMetadata | None`.
  - Guard `is_trained`, `fit`, `update_model`, and `analyze` classifier snapshot read with `self._lock`.

- [ ] **Step 4: Run test to verify GREEN**

Run: `.venv\Scripts\pytest.exe backend\tests\integration\test_sklearn_analyzer.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/pyproject.toml backend/src/tutoring/infrastructure/ml/model_store.py backend/src/tutoring/infrastructure/ml/sklearn_analyzer.py backend/tests/integration/test_sklearn_analyzer.py
git commit -m "feat(ml): add atomic ModelArtifactStore and thread-safe lazy SklearnPedagogicalAnalyzer"
```

---

### Task 6: Resource-Bounded `PedagogicalModelTrainer` & Quality Gating

**Files:**
- Create: `backend/src/tutoring/infrastructure/ml/trainer.py`
- Test: `backend/tests/integration/test_ml_trainer.py`

**Interfaces:**
- Consumes:
  - `StudentRepository`, `SessionRepository`, `CatalogRepository`
  - `TrainingDatasetBuilder` (Task 2), `ModelArtifactStore` (Task 5), `SklearnPedagogicalAnalyzer` (Task 5)
- Produces:
  - `TrainingStatus(str, Enum)`
  - `TrainingReport(status: TrainingStatus, sample_count: int, cv_f1_macro: float | None = None, baseline_f1_macro: float | None = None, model_version: int | None = None, reason: str = "")`
  - `PedagogicalModelTrainer(..., min_samples: int = 20, cv_folds: int = 3, min_f1_score: float = 0.55, estimator_factory: Callable[[], Any] | None = None, db_lock: threading.RLock | None = None)` with `.train_and_activate() -> TrainingReport`

- [ ] **Step 1: Write failing tests for trainer lifecycle, quality gating, unchanged skip, and single-class guard**

Create `backend/tests/integration/test_ml_trainer.py`:

```python
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from sklearn.dummy import DummyClassifier

from tutoring.application.fakes import (
    InMemoryCatalogRepository,
    InMemorySessionRepository,
    InMemoryStudentRepository,
)
from tutoring.domain.entities.catalog import ExerciseType, Subject, Topic
from tutoring.domain.entities.session import TutoringSession
from tutoring.domain.entities.student import Student
from tutoring.domain.enums import AttemptOutcome, ErrorCause
from tutoring.domain.value_objects.attempt import ExerciseAttempt
from tutoring.domain.value_objects.exam_goal import ExamGoal, ExamResult
from tutoring.infrastructure.ml.model_store import ModelArtifactStore
from tutoring.infrastructure.ml.sklearn_analyzer import SklearnPedagogicalAnalyzer
from tutoring.infrastructure.ml.trainer import PedagogicalModelTrainer, TrainingStatus


def _seed_repos(n_per_class: int, include_high: bool = True):
    student_repo = InMemoryStudentRepository()
    catalog_repo = InMemoryCatalogRepository()
    session_repo = InMemorySessionRepository()
    subject = Subject(id=uuid4(), name="Matemáticas")
    topic = Topic(id=uuid4(), subject_id=subject.id, name="Álgebra")
    ex = ExerciseType(id=uuid4(), topic_id=topic.id, name="Ecuaciones")
    catalog_repo.save_subject(subject)
    catalog_repo.save_topic(topic)
    catalog_repo.save_exercise_type(ex)

    base = datetime(2026, 10, 1, 17, 0, tzinfo=timezone.utc)
    classes = [0, 1] if include_high else [0]
    for cls in classes:
        student = Student(id=uuid4(), full_name=f"Alumno {cls}", academic_level="4º ESO")
        for idx in range(n_per_class):
            dt = base + timedelta(days=idx)
            outcome = AttemptOutcome.FAILURE if cls == 1 else AttemptOutcome.SUCCESS
            cause = ErrorCause.CONCEPT if cls == 1 else None
            session_repo.save(
                TutoringSession(
                    id=uuid4(),
                    student_id=student.id,
                    occurred_at=dt,
                    duration_minutes=60,
                    attempts=[ExerciseAttempt(ex.id, outcome, cause)],
                )
            )
            if idx % 3 == 0:
                student.add_exam_goal(
                    ExamGoal(
                        id=uuid4(),
                        subject_id=subject.id,
                        title=f"Exam {cls}-{idx}",
                        exam_date=dt.date(),
                        result=ExamResult(score=3.0 if cls == 1 else 8.5, recorded_at=dt),
                    ),
                    today=dt.date(),
                )
        student_repo.save(student)
    return student_repo, session_repo, catalog_repo


def test_trainer_skips_insufficient_and_single_class_datasets(tmp_path: Path) -> None:
    s_repo, sess_repo, cat_repo = _seed_repos(n_per_class=5, include_high=True)
    store = ModelArtifactStore(tmp_path)
    analyzer = SklearnPedagogicalAnalyzer(model_store=store)
    trainer = PedagogicalModelTrainer(s_repo, sess_repo, cat_repo, analyzer, store, min_samples=20)
    rep_small = trainer.train_and_activate()
    assert rep_small.status == TrainingStatus.SKIPPED_INSUFFICIENT_DATA
    assert analyzer.is_trained is False

    s_repo2, sess_repo2, cat_repo2 = _seed_repos(n_per_class=22, include_high=False)
    trainer2 = PedagogicalModelTrainer(s_repo2, sess_repo2, cat_repo2, analyzer, store, min_samples=20)
    rep_single = trainer2.train_and_activate()
    assert rep_single.status == TrainingStatus.SKIPPED_SINGLE_CLASS
    assert analyzer.is_trained is False


def test_trainer_trains_persists_skips_unchanged_and_rejects_poor_quality(tmp_path: Path) -> None:
    s_repo, sess_repo, cat_repo = _seed_repos(n_per_class=12, include_high=True)  # 24 samples
    store = ModelArtifactStore(tmp_path)
    analyzer = SklearnPedagogicalAnalyzer(model_store=store)
    trainer = PedagogicalModelTrainer(s_repo, sess_repo, cat_repo, analyzer, store, min_samples=20)

    rep1 = trainer.train_and_activate()
    assert rep1.status == TrainingStatus.TRAINED
    assert rep1.model_version == 1
    assert rep1.cv_f1_macro is not None and rep1.baseline_f1_macro is not None
    assert rep1.cv_f1_macro > rep1.baseline_f1_macro
    assert analyzer.is_trained is True

    # Re-running with identical data short-circuits without retraining
    rep2 = trainer.train_and_activate()
    assert rep2.status == TrainingStatus.SKIPPED_UNCHANGED

    # Poor quality candidate (DummyClassifier) gets rejected and keeps version 1 intact
    poor_trainer = PedagogicalModelTrainer(
        s_repo,
        sess_repo,
        cat_repo,
        analyzer,
        store,
        min_samples=20,
        estimator_factory=lambda: DummyClassifier(strategy="most_frequent"),
    )
    # Bump dataset slightly by adding 1 new session to avoid hash short-circuit
    student = list(s_repo.list_all())[0]
    ex_id = cat_repo.get_snapshot().exercise_types[0].id
    sess_repo.save(
        TutoringSession(
            id=uuid4(),
            student_id=student.id,
            occurred_at=datetime(2026, 11, 20, 17, 0, tzinfo=timezone.utc),
            duration_minutes=60,
            attempts=[ExerciseAttempt(ex_id, AttemptOutcome.SUCCESS)],
        )
    )
    rep_rejected = poor_trainer.train_and_activate()
    assert rep_rejected.status == TrainingStatus.REJECTED_QUALITY
    assert analyzer.metadata is not None and analyzer.metadata.version == 1
```

- [ ] **Step 2: Run test to verify RED**

Run: `.venv\Scripts\pytest.exe backend\tests\integration\test_ml_trainer.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'tutoring.infrastructure.ml.trainer'`).

- [ ] **Step 3: Implement `PedagogicalModelTrainer` in `backend/src/tutoring/infrastructure/ml/trainer.py`**

Key implementation details:
- Default `estimator_factory`: `RandomForestClassifier(n_estimators=50, max_depth=5, min_samples_leaf=2, n_jobs=1, random_state=42)`.
- Acquire `db_lock` only while fetching `list_all()`, `list_by_student()`, and `get_snapshot()`, then release lock before `dataset_builder.build(...)` and ML computation.
- Check `dataset_hash` against `self._analyzer.metadata` (or `self._model_store.load_metadata()` if not loaded).
- Validate `len(y) >= self._min_samples`, `len(counts) >= 2`, and `min(counts.values()) >= self._cv_folds`.
- Evaluate candidate vs `DummyClassifier(strategy="most_frequent")` with `StratifiedKFold(n_splits=self._cv_folds, shuffle=True, random_state=42)` and `scoring="f1_macro"`, `n_jobs=1`.
- On passing gate (`cv_f1 > baseline_f1 and cv_f1 >= self._min_f1_score`), fit final estimator on full `(X, y)`, increment `version`, save via `model_store.save(...)`, and call `analyzer.update_model(...)`.

- [ ] **Step 4: Run test to verify GREEN**

Run: `.venv\Scripts\pytest.exe backend\tests\integration\test_ml_trainer.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/src/tutoring/infrastructure/ml/trainer.py backend/tests/integration/test_ml_trainer.py
git commit -m "feat(ml): add resource-bounded PedagogicalModelTrainer with CV quality gating"
```

---

### Task 7: Coalescing `BackgroundTrainingCoordinator` (Debounce + `max_workers=1`)

**Files:**
- Create: `backend/src/tutoring/infrastructure/ml/background_coordinator.py`
- Test: `backend/tests/integration/test_background_coordinator.py`

**Interfaces:**
- Consumes: `TrainingTriggerPort`, `PedagogicalModelTrainer`, `TrainingReport` (Task 6)
- Produces:
  - `BackgroundTrainingCoordinator(trainer: PedagogicalModelTrainer, debounce_seconds: float = 5.0, burst_threshold: int = 10)`
  - `.notify_new_data() -> None`, `.flush(timeout: float = 30.0) -> TrainingReport | None`, `.shutdown(wait: bool = False) -> None`
  - Properties: `.pending_events: int`, `.is_training: bool`, `.last_report: TrainingReport | None`

- [ ] **Step 1: Write failing tests for debounce coalescing, burst flush, in-flight trailing re-run, and error isolation**

Create `backend/tests/integration/test_background_coordinator.py`:

```python
import threading
import time
from tutoring.infrastructure.ml.background_coordinator import BackgroundTrainingCoordinator
from tutoring.infrastructure.ml.trainer import TrainingReport, TrainingStatus


class _StubTrainer:
    def __init__(self, fail: bool = False, wait_for_release: bool = False) -> None:
        self.calls = 0
        self._fail = fail
        self._wait_for_release = wait_for_release
        self.started_event = threading.Event()
        self.release_event = threading.Event()

    def train_and_activate(self) -> TrainingReport:
        self.calls += 1
        self.started_event.set()
        if self._wait_for_release and self.calls == 1:
            self.release_event.wait(timeout=2.0)
        if self._fail:
            raise RuntimeError("boom")
        return TrainingReport(status=TrainingStatus.TRAINED, sample_count=20, model_version=self.calls)


def test_coordinator_coalesces_events_within_debounce_window() -> None:
    trainer = _StubTrainer()
    coord = BackgroundTrainingCoordinator(trainer=trainer, debounce_seconds=0.08, burst_threshold=10)  # type: ignore[arg-type]
    try:
        for _ in range(5):
            coord.notify_new_data()
        assert coord.pending_events == 5
        time.sleep(0.25)
        assert trainer.calls == 1
        assert coord.last_report is not None
        assert coord.last_report.status == TrainingStatus.TRAINED
    finally:
        coord.shutdown(wait=True)


def test_coordinator_triggers_immediately_on_burst_threshold_and_handles_errors() -> None:
    trainer = _StubTrainer(fail=True)
    coord = BackgroundTrainingCoordinator(trainer=trainer, debounce_seconds=30.0, burst_threshold=3)  # type: ignore[arg-type]
    try:
        coord.notify_new_data()
        coord.notify_new_data()
        assert trainer.calls == 0
        coord.notify_new_data()  # hits burst_threshold=3
        report = coord.flush(timeout=2.0)
        assert trainer.calls == 1
        assert report is not None
        assert report.status == TrainingStatus.FAILED
    finally:
        coord.shutdown(wait=True)


def test_coordinator_coalesces_events_arriving_while_in_flight() -> None:
    trainer = _StubTrainer(wait_for_release=True)
    coord = BackgroundTrainingCoordinator(trainer=trainer, debounce_seconds=0.05, burst_threshold=10)  # type: ignore[arg-type]
    try:
        coord.notify_new_data()
        assert trainer.started_event.wait(timeout=2.0)
        # Multiple events while job 1 is running coalesce into a single follow-up run
        for _ in range(4):
            coord.notify_new_data()
        trainer.release_event.set()
        time.sleep(0.2)
        assert trainer.calls == 2
    finally:
        coord.shutdown(wait=True)
```

- [ ] **Step 2: Run test to verify RED**

Run: `.venv\Scripts\pytest.exe backend\tests\integration\test_background_coordinator.py -v`
Expected: FAIL (`ModuleNotFoundError: No module named 'tutoring.infrastructure.ml.background_coordinator'`).

- [ ] **Step 3: Implement `BackgroundTrainingCoordinator` in `backend/src/tutoring/infrastructure/ml/background_coordinator.py`**

- Use `ThreadPoolExecutor(max_workers=1, thread_name_prefix="ml-trainer")` and daemon `threading.Timer` guarded by `_state_lock = threading.Lock()`.
- Track `_pending_events`, `_timer`, `_in_flight`, `_dirty_while_in_flight`, `_current_future`, `_last_report`, `_shutdown`.
- If `notify_new_data()` fires while `_in_flight` is True, set `_dirty_while_in_flight = True` and return immediately; when `_run_job()` finishes in `finally:`, schedule one trailing debounce pass if `_dirty_while_in_flight` is True and not shutdown.
- Catch exceptions in `_run_job()`, log with `logging.getLogger(__name__).exception(...)`, and store `TrainingReport(status=TrainingStatus.FAILED, sample_count=0, reason=str(exc))`.
- Implement `flush(timeout: float = 30.0)` to cancel any timer, submit immediately if `_pending_events > 0` and not `_in_flight`, wait on `_current_future.result(timeout=timeout)` (and loop once if `_dirty_while_in_flight`), and return `_last_report`.

- [ ] **Step 4: Run test to verify GREEN**

Run: `.venv\Scripts\pytest.exe backend\tests\integration\test_background_coordinator.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/src/tutoring/infrastructure/ml/background_coordinator.py backend/tests/integration/test_background_coordinator.py
git commit -m "feat(ml): add coalescing BackgroundTrainingCoordinator with single-worker executor"
```

---

### Task 8: FastAPI Wiring, `lifespan`, `POST .../result` & End-to-End Verification

**Files:**
- Modify: `backend/src/tutoring/presentation/api/app.py:1-282`
- Modify: `backend/src/tutoring/presentation/api/main.py:1-7`
- Modify: `backend/tests/integration/test_students_api.py`
- Create: `backend/tests/integration/test_ml_training_e2e_api.py`

**Interfaces:**
- Consumes: `BackgroundTrainingCoordinator` (Task 7), `PedagogicalModelTrainer` (Task 6), `SklearnPedagogicalAnalyzer` & `ModelArtifactStore` (Task 5), `RecordExamResultDTO` & `ManageStudentsUseCase.record_exam_result` (Task 3)
- Produces:
  - `create_app(db_path: str = ":memory:", model_dir: str | Path | None = None, debounce_seconds: float = 5.0, burst_threshold: int = 10, min_training_samples: int = 20) -> FastAPI`
  - `POST /api/students/{student_id}/exam-goals/{goal_id}/result` returning `ExamGoalDTO` (201 Created; 404/409/422 via domain handlers)

- [ ] **Step 1: Write failing API tests for `POST .../exam-goals/{goal_id}/result` and E2E auto-training pipeline**

Append to `backend/tests/integration/test_students_api.py`:

```python
@pytest.mark.asyncio
async def test_record_exam_goal_result_api_endpoint_and_errors() -> None:
    app = create_app(":memory:")
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            s_res = await client.post("/api/students", json={"full_name": "Inés", "academic_level": "1º Bach"})
            student_id = s_res.json()["id"]
            sub_res = await client.post("/api/catalog/subjects", json={"name": "Química"})
            subject_id = sub_res.json()["id"]
            g_res = await client.post(
                f"/api/students/{student_id}/exam-goals",
                json={"subject_id": subject_id, "title": "Estequiometría", "exam_date": "2026-11-25"},
            )
            goal_id = g_res.json()["id"]

            # Invalid score (> max_score) -> 422
            bad_res = await client.post(
                f"/api/students/{student_id}/exam-goals/{goal_id}/result",
                json={"score": 11.0, "max_score": 10.0},
            )
            assert bad_res.status_code == 422

            # Valid grade -> 201
            ok_res = await client.post(
                f"/api/students/{student_id}/exam-goals/{goal_id}/result",
                json={"score": 4.2, "max_score": 10.0, "notes": "Fallos en moles"},
            )
            assert ok_res.status_code == 201
            body = ok_res.json()
            assert body["result"]["score"] == 4.2
            assert body["result"]["is_passing"] is False

            # Duplicate result -> 409
            dup_res = await client.post(
                f"/api/students/{student_id}/exam-goals/{goal_id}/result",
                json={"score": 7.0},
            )
            assert dup_res.status_code == 409
    finally:
        app.state.training_coordinator.shutdown(wait=True)
```

Create `backend/tests/integration/test_ml_training_e2e_api.py`:

```python
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from tutoring.presentation.api.app import create_app


@pytest.mark.asyncio
async def test_e2e_api_auto_trains_model_and_skips_empty_session_retrain(tmp_path: Path) -> None:
    model_dir = tmp_path / "models"
    db_file = tmp_path / "tutoring.sqlite3"
    app = create_app(
        db_path=str(db_file),
        model_dir=model_dir,
        debounce_seconds=0.05,
        burst_threshold=50,
        min_training_samples=20,
    )
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            sub_id = (await client.post("/api/catalog/subjects", json={"name": "Matemáticas"})).json()["id"]
            top_id = (await client.post("/api/catalog/topics", json={"subject_id": sub_id, "name": "Álgebra"})).json()["id"]
            ex_id = (await client.post("/api/catalog/exercise-types", json={"topic_id": top_id, "name": "Ecuaciones"})).json()["id"]

            # Create 2 students: one passing (target=0), one failing (target=1) across 11 sessions each (>=22 samples)
            s_pass = (await client.post("/api/students", json={"full_name": "Clara", "academic_level": "4º ESO"})).json()["id"]
            s_fail = (await client.post("/api/students", json={"full_name": "Mateo", "academic_level": "4º ESO"})).json()["id"]
            base_dt = datetime(2026, 10, 1, 17, 0, tzinfo=timezone.utc)

            for i in range(11):
                dt = (base_dt + timedelta(days=i)).isoformat()
                await client.post(
                    f"/api/students/{s_pass}/sessions",
                    json={"occurred_at": dt, "duration_minutes": 60, "attempts": [{"exercise_type_id": ex_id, "outcome": "SUCCESS"}]},
                )
                await client.post(
                    f"/api/students/{s_fail}/sessions",
                    json={
                        "occurred_at": dt,
                        "duration_minutes": 60,
                        "attempts": [{"exercise_type_id": ex_id, "outcome": "FAILURE", "error_cause": "CONCEPT"}],
                    },
                )

            # Record exam goals + results (triggers automatic retraining)
            g_fail = (
                await client.post(
                    f"/api/students/{s_fail}/exam-goals",
                    json={"subject_id": sub_id, "title": "Global", "exam_date": "2026-11-20"},
                )
            ).json()["id"]
            await client.post(
                f"/api/students/{s_fail}/exam-goals/{g_fail}/result",
                json={"score": 3.5, "recorded_at": "2026-11-20T18:00:00Z"},
            )

            report = app.state.training_coordinator.flush(timeout=10.0)
            assert report is not None
            assert report.status.value == "TRAINED"
            assert (model_dir / "active_analyzer.joblib").exists()

            diag_res = await client.get(f"/api/students/{s_fail}/diagnostic")
            assert diag_res.status_code == 200
            assert diag_res.json()["analyzer_name"] == "SklearnPedagogicalAnalyzerV1"

            # Recording a zero-attempt session does not change dataset or trigger retraining
            empty_res = await client.post(
                f"/api/students/{s_pass}/sessions",
                json={"occurred_at": "2026-11-21T17:00:00Z", "duration_minutes": 30, "attempts": []},
            )
            assert empty_res.status_code == 201
            assert app.state.training_coordinator.pending_events == 0

        # Restart app pointing to same DB + model_dir -> lazy-loads persisted model immediately
        app2 = create_app(db_path=str(db_file), model_dir=model_dir)
        try:
            async with AsyncClient(transport=ASGITransport(app=app2), base_url="http://test") as client2:
                diag2 = await client2.get(f"/api/students/{s_fail}/diagnostic")
                assert diag2.status_code == 200
                assert diag2.json()["analyzer_name"] == "SklearnPedagogicalAnalyzerV1"
        finally:
            app2.state.training_coordinator.shutdown(wait=True)
    finally:
        app.state.training_coordinator.shutdown(wait=True)
```

- [ ] **Step 2: Run tests to verify RED**

Run: `.venv\Scripts\pytest.exe backend\tests\integration\test_students_api.py backend\tests\integration\test_ml_training_e2e_api.py -v`
Expected: FAIL (`404 Not Found` on `/result` and unexpected keyword `model_dir` in `create_app`).

- [ ] **Step 3: Wire `create_app`, `lifespan`, `POST .../result`, and `main.py`**

- In `backend/src/tutoring/presentation/api/app.py`:
  - Update `create_app(...)` signature with `model_dir: str | Path | None = None, debounce_seconds: float = 5.0, burst_threshold: int = 10, min_training_samples: int = 20`.
  - Create shared `db_lock = threading.RLock()` and pass to `SqliteCatalogRepository`, `SqliteStudentRepository`, `SqliteSessionRepository`.
  - Initialize `model_store`, `SklearnPedagogicalAnalyzer(model_store=model_store)`, `PedagogicalModelTrainer(...)`, `BackgroundTrainingCoordinator(...)`.
  - Pass `training_trigger=training_coordinator` to `ManageStudentsUseCase` and `RecordSessionUseCase`.
  - Attach `app.state.training_coordinator` and `app.state.analyzer` and register FastAPI `lifespan` context manager calling `training_coordinator.shutdown(wait=False)` on exit.
  - Add `RecordExamResultPayload` (`score: float = Field(ge=0.0)`, `max_score: float = Field(default=10.0, gt=0.0)`, `recorded_at: datetime | None = None`, `notes: str = ""`) and endpoint `POST /api/students/{student_id}/exam-goals/{goal_id}/result` (`status_code=status.HTTP_201_CREATED`, `response_model=ExamGoalDTO`).
- In `backend/src/tutoring/presentation/api/main.py`:
  - Read `TUTORING_DB_PATH` (default `"tutoring.sqlite3"`) and `TUTORING_MODEL_DIR` (default `"models"`) and pass to `create_app(...)`.

- [ ] **Step 4: Run full backend test suite + strict mypy**

Run: `.venv\Scripts\pytest.exe backend -v && .venv\Scripts\mypy.exe backend\src`
Expected: All tests PASS and `mypy` reports `Success: no issues found`.

- [ ] **Step 5: Commit**

```bash
git add backend/src/tutoring/presentation/api/app.py backend/src/tutoring/presentation/api/main.py backend/tests/integration/test_students_api.py backend/tests/integration/test_ml_training_e2e_api.py
git commit -m "feat(api): wire automatic ML training pipeline and exam-goal result endpoint"
```
