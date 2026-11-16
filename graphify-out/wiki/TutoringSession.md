# TutoringSession

> God node · 65 connections · `backend/src/tutoring/domain/entities/session.py`

**Community:** [Community 3](Community_3.md)

## Connections by Relation

### calls
- .execute() `EXTRACTED`

### contains
- session.py `EXTRACTED`

### imports
- heuristic_analyzer.py `EXTRACTED`
- feature_extractor.py `EXTRACTED`
- scoring.py `EXTRACTED`
- repositories.py `EXTRACTED`
- fakes.py `EXTRACTED`
- sklearn_analyzer.py `EXTRACTED`
- record_session.py `EXTRACTED`
- sqlite_session_repo.py `EXTRACTED`
- analyzer.py `EXTRACTED`
- entities/__init__.py `EXTRACTED`

### method
- .id() `EXTRACTED`
- .attempts() `EXTRACTED`
- .__init__() `EXTRACTED`
- .failure_rate() `EXTRACTED`
- .update_duration() `EXTRACTED`
- .student_id() `EXTRACTED`
- .occurred_at() `EXTRACTED`
- .duration_minutes() `EXTRACTED`
- .session_notes() `EXTRACTED`
- .record_attempt() `EXTRACTED`
- .update_notes() `EXTRACTED`
- .__eq__() `EXTRACTED`
- .__repr__() `EXTRACTED`

### rationale_for
- Aggregate root capturing a tutoring session and its exercise attempts. `EXTRACTED`

### references
- .analyze() `EXTRACTED`
- .extract_subject_features() `EXTRACTED`
- ._to_dto() `EXTRACTED`
- .extract_student_features() `EXTRACTED`
- .analyze() `EXTRACTED`
- .save() `EXTRACTED`
- .analyze() `EXTRACTED`
- ._hydrate_session() `EXTRACTED`
- .list_by_student() `EXTRACTED`
- .list_by_student() `EXTRACTED`
- .get_by_id() `EXTRACTED`
- .list_by_student() `EXTRACTED`
- .save() `EXTRACTED`
- .get_by_id() `EXTRACTED`
- .save() `EXTRACTED`
- .get_by_id() `EXTRACTED`

### uses
- [ExerciseAttempt](ExerciseAttempt.md) `INFERRED`
- HeuristicPedagogicalAnalyzer `INFERRED`
- test_sqlite_session_persistence_lifecycle() `INFERRED`
- FeatureExtractor `INFERRED`
- RecordSessionUseCase `INFERRED`
- SessionRepository `INFERRED`
- SklearnPedagogicalAnalyzer `INFERRED`
- test_feature_extractor_extracts_student_and_subject_vectors() `INFERRED`
- SqliteSessionRepository `INFERRED`
- test_sklearn_analyzer_trained_inference() `INFERRED`
- PedagogicalAnalyzerPort `INFERRED`
- test_sklearn_analyzer_fallback_when_untrained() `INFERRED`
- test_analyzer_identifies_weak_exercise_types_excluding_mastered_ones() `INFERRED`
- test_analyzer_propagates_subject_and_overall_trends_with_regression_bonus() `INFERRED`
- test_subject_priority_ranking_combines_failure_rate_and_exam_urgency() `INFERRED`
- test_analyzer_subject_weighted_failure_rate_reflects_recency() `INFERRED`
- test_exam_alerts_capture_readiness_risk_and_unpracticed_subjects() `INFERRED`
- collect_timed_attempts() `INFERRED`
- InMemorySessionRepository `INFERRED`
- test_in_memory_session_repository() `INFERRED`
- *…and 3 more `uses` connection(s) not listed (lowest-degree first to go)*

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*