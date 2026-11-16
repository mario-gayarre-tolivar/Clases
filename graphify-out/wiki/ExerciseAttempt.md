# ExerciseAttempt

> God node · 41 connections · `backend/src/tutoring/domain/value_objects/attempt.py`

**Community:** [Community 3](Community_3.md)

## Connections by Relation

### calls
- .execute() `EXTRACTED`
- ._hydrate_session() `EXTRACTED`
- _ta() `EXTRACTED`

### contains
- attempt.py `EXTRACTED`

### imports
- scoring.py `EXTRACTED`
- session.py `EXTRACTED`
- record_session.py `EXTRACTED`
- sqlite_session_repo.py `EXTRACTED`
- value_objects/__init__.py `EXTRACTED`

### method
- .severity_weight() `EXTRACTED`
- .__post_init__() `EXTRACTED`

### rationale_for
- Immutable record of a student's attempt on a specific exercise type. `EXTRACTED`

### references
- .attempts() `EXTRACTED`
- .__init__() `EXTRACTED`
- .record_attempt() `EXTRACTED`

### uses
- [TutoringSession](TutoringSession.md) `INFERRED`
- [AttemptOutcome](AttemptOutcome.md) `INFERRED`
- [ErrorCause](ErrorCause.md) `INFERRED`
- test_sqlite_session_persistence_lifecycle() `INFERRED`
- TimedAttempt `INFERRED`
- RecordSessionUseCase `INFERRED`
- test_feature_extractor_extracts_student_and_subject_vectors() `INFERRED`
- SqliteSessionRepository `INFERRED`
- test_sklearn_analyzer_trained_inference() `INFERRED`
- test_sklearn_analyzer_fallback_when_untrained() `INFERRED`
- test_analyzer_identifies_weak_exercise_types_excluding_mastered_ones() `INFERRED`
- test_analyzer_propagates_subject_and_overall_trends_with_regression_bonus() `INFERRED`
- test_subject_priority_ranking_combines_failure_rate_and_exam_urgency() `INFERRED`
- test_analyzer_subject_weighted_failure_rate_reflects_recency() `INFERRED`
- test_exam_alerts_capture_readiness_risk_and_unpracticed_subjects() `INFERRED`
- test_in_memory_session_repository() `INFERRED`
- test_session_failure_rate_for_empty_and_mixed_attempts() `INFERRED`
- test_session_normalizes_notes_and_exposes_immutable_attempts() `INFERRED`
- test_compute_learning_trend_covers_all_classifications() `INFERRED`
- test_recency_weight_and_weighted_failure_rate_prioritize_recent_errors() `INFERRED`
- *…and 6 more `uses` connection(s) not listed (lowest-degree first to go)*

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*