# Diseño: Pipeline de Reentrenamiento Automático y Eficiente para Modelo Pedagógico ML

## 1. Intención y Por Qué
El sistema pedagógico actual cuenta con un adaptador de Machine Learning clásico (`SklearnPedagogicalAnalyzer`) que delega en un modelo en memoria sin persistencia ni reentrenamiento basado en resultados reales.
El objetivo de este proyecto es dotar a la plataforma de un ciclo continuo de aprendizaje automático a partir de resultados empíricos (calificaciones reales de exámenes y tasas de éxito/fallo acumuladas por tipos de ejercicio), garantizando que el consumo de recursos sea estrictamente controlado y no degrade el rendimiento de la API ni sature la máquina.

---

## 2. Metas, No-Metas y Anti-Metas

### Metas (Goals)
1. **Entrenamiento Supervisado con Evidencia Empírica**: Generar datasets de entrenamiento a partir de datos reales:
   - Registro de calificaciones y resultados en exámenes (`ExamResult` asociado a `ExamGoal` existente mediante `POST /api/students/{id}/exam-goals/{goal_id}/result`).
   - Tasas de acierto/fallo y desglose de causas de error (`ErrorCause`) por `ExerciseType`.
   - **Regla de Etiquetado Supervisado (Ground Truth híbrido)**: Una muestra se etiqueta con prioridad ALTA (`target = 1`) si el alumno suspendió el examen asociado (`score < 5.0`) O si la tasa de fallo ponderada en las sesiones recientes de la asignatura supera el 40% (`weighted_failure_rate > 0.40`). En caso contrario, se etiqueta como NORMAL (`target = 0`).
2. **Reentrenamiento Automático Eficiente**:
   - Disparo tras la ingesta de nuevos resultados (registro de sesión de ejercicios o calificación de examen).
   - Control estricto de recursos mediante **estrategia de coalescencia / debouncing** y **umbral mínimo de muestras** ($N \ge 20$ con validación cruzada) para evitar entrenar con cada micro-cambio.
   - Ejecución asíncrona no bloqueante mediante un `ThreadPoolExecutor(max_workers=1)` dedicado a tareas de ML en segundo plano.
3. **Persistencia y Versionado de Modelos**:
   - Serialización atómica en disco (usando `joblib`) con metadatos de versión y fecha (`active_analyzer.joblib` y `active_analyzer_meta.json`).
   - Hot-reloading seguro en el runtime del analizador.
4. **Gating de Calidad y Fallback Seguro**:
   - Validación cruzada previa al despliegue del modelo (si las métricas no superan la línea base o el volumen de datos es insuficiente, se conserva el modelo previo o se mantiene el fallback heurístico).

### No-Metas (Non-Goals)
- No se implementarán arquitecturas pesadas de deep learning ni GPUs; se mantiene `scikit-learn` clásico optimizado para tabular/CPU.
- No se incorporarán dependencias pesadas de infraestructura como Redis, Celery o Kafka; se resolverá nativamente en el runtime de Python y SQLite.
- No se creará interfaz de gestión compleja de MLOps en el frontend en esta fase (solo consumo transparente del modelo actualizado).

### Anti-Metas (Anti-Goals)
- **Bloqueo del hilo HTTP**: Ningún request de registro de sesión o examen debe esperar a que el modelo termine de entrenar.
- **Sobrecarga de CPU/Disco (Train Thrashing)**: Jamás ejecutar reentrenamientos concurrentes múltiples ni bucles de entrenamiento en ráfagas.

---

## 3. Restricciones y Decisiones de Arquitectura

1. **Gestión de Carga (Resource Guardrails)**:
   - **Debounce / Coalescencia**: Cuando llega un evento de nuevos datos, se programa el reentrenamiento con un retardo de 5 segundos o tras acumular una ráfaga pendiente de eventos. Si llegan más eventos en la ventana, se fusionan en un único job.
   - **Worker Unitario**: `ThreadPoolExecutor(max_workers=1)` para que el impacto en CPU sea de un solo núcleo y nunca compita contra los endpoints de la API.
2. **Modelo de Datos y Dominio**:
   - Incorporación de `ExamResult` vinculada al estudiante y a su `ExamGoal`.
   - Nuevo endpoint de API: `POST /api/students/{id}/exam-goals/{goal_id}/result`.
   - Repositorio / consultas para extracción de dataset histórico (features previas vs. etiqueta objetivo híbrida).
3. **Persistencia de Modelos**:
   - Almacenamiento en directorio configurable (ej. `backend/models/active_analyzer.joblib` y `active_analyzer_meta.json`).
   - Carga perezosa (lazy load) y swap atómico en memoria.

---

## 4. Partes Decididas y Delegadas al Constructor

- **Decidido**:
  - Reentrenamiento automático en segundo plano con coalescencia (debounce).
  - Etiquetado híbrido (nota < 5.0 o fallo > 40%).
  - Endpoint `POST /api/students/{id}/exam-goals/{goal_id}/result`.
  - Persistencia en disco de artefactos con `joblib` y fallback heurístico garantizado.
- **Delega al Constructor**:
  - Ajuste fino de hiperparámetros de `RandomForestClassifier` / `LogisticRegression`.
  - Configuración exacta del directorio de artefactos en settings de la aplicación.
