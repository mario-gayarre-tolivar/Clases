# ErrorCause

> God node · 39 connections · `backend/src/tutoring/domain/enums.py`

**Community:** [Community 3](Community_3.md)

## Connections by Relation

### calls
- ._hydrate_session() `EXTRACTED`

### contains
- enums.py `EXTRACTED`

### imports
- app.py `EXTRACTED`
- dtos.py `EXTRACTED`
- feature_extractor.py `EXTRACTED`
- scoring.py `EXTRACTED`
- attempt.py `EXTRACTED`
- sqlite_session_repo.py `EXTRACTED`
- diagnostic.py `EXTRACTED`

### inherits
- Enum `EXTRACTED`
- str `EXTRACTED`

### rationale_for
- Pedagogical root cause behind a partial or failed attempt. `EXTRACTED`

### references
- ._compute_cause_ratios() `EXTRACTED`

### uses
- [ExerciseAttempt](ExerciseAttempt.md) `INFERRED`
- test_generate_student_diagnostic_orchestration() `INFERRED`
- test_sqlite_session_persistence_lifecycle() `INFERRED`
- test_record_session_validates_student_and_exercise_types_and_saves() `INFERRED`
- FeatureExtractor `INFERRED`
- test_feature_extractor_extracts_student_and_subject_vectors() `INFERRED`
- SqliteSessionRepository `INFERRED`
- test_sklearn_analyzer_trained_inference() `INFERRED`
- test_sklearn_analyzer_fallback_when_untrained() `INFERRED`
- test_analyzer_identifies_weak_exercise_types_excluding_mastered_ones() `INFERRED`
- test_analyzer_propagates_subject_and_overall_trends_with_regression_bonus() `INFERRED`
- test_subject_priority_ranking_combines_failure_rate_and_exam_urgency() `INFERRED`
- test_analyzer_subject_weighted_failure_rate_reflects_recency() `INFERRED`
- WeakExerciseType `INFERRED`
- test_session_failure_rate_for_empty_and_mixed_attempts() `INFERRED`
- compute_dominant_error_cause() `INFERRED`
- ExerciseAttemptInputDTO `INFERRED`
- test_compute_learning_trend_covers_all_classifications() `INFERRED`
- test_recency_weight_and_weighted_failure_rate_prioritize_recent_errors() `INFERRED`
- test_dominant_error_cause_uses_recency_and_severity_weights() `INFERRED`
- *…and 6 more `uses` connection(s) not listed (lowest-degree first to go)*

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*