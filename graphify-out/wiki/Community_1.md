# Community 1

> 85 nodes · cohesion 0.07

## Key Concepts

- **AcademicCatalogSnapshot** (53 connections) — `backend/src/tutoring/domain/entities/catalog.py`
- **Subject** (49 connections) — `backend/src/tutoring/domain/entities/catalog.py`
- **ExerciseType** (47 connections) — `backend/src/tutoring/domain/entities/catalog.py`
- **Topic** (47 connections) — `backend/src/tutoring/domain/entities/catalog.py`
- **test_sqlite_session_persistence_lifecycle()** (23 connections) — `backend/tests/integration/test_sqlite_session_repo.py`
- **.id()** (20 connections) — `backend/src/tutoring/domain/entities/student.py`
- **SqliteCatalogRepository** (20 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_catalog_repo.py`
- **require_non_empty()** (18 connections) — `backend/src/tutoring/domain/validation.py`
- **.get_subject()** (16 connections) — `backend/src/tutoring/domain/entities/catalog.py`
- **.resolve_exercise_path()** (16 connections) — `backend/src/tutoring/domain/entities/catalog.py`
- **test_sqlite_catalog_persistence_and_snapshot()** (16 connections) — `backend/tests/integration/test_sqlite_catalog_repo.py`
- **sqlite_catalog_repo.py** (15 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_catalog_repo.py`
- **test_sklearn_analyzer_trained_inference()** (15 connections) — `backend/tests/integration/test_sklearn_analyzer.py`
- **test_sklearn_analyzer_fallback_when_untrained()** (14 connections) — `backend/tests/integration/test_sklearn_analyzer.py`
- **test_snapshot_resolves_hierarchy_and_listings()** (14 connections) — `backend/tests/unit/domain/test_catalog_entities.py`
- **test_catalog_entities.py** (13 connections) — `backend/tests/unit/domain/test_catalog_entities.py`
- **test_analyzer_identifies_weak_exercise_types_excluding_mastered_ones()** (13 connections) — `backend/tests/unit/domain/test_heuristic_analyzer.py`
- **test_analyzer_propagates_subject_and_overall_trends_with_regression_bonus()** (13 connections) — `backend/tests/unit/domain/test_heuristic_analyzer.py`
- **test_subject_priority_ranking_combines_failure_rate_and_exam_urgency()** (13 connections) — `backend/tests/unit/domain/test_heuristic_analyzer.py`
- **test_analyzer_subject_weighted_failure_rate_reflects_recency()** (12 connections) — `backend/tests/unit/domain/test_heuristic_analyzer.py`
- **test_exam_alerts_capture_readiness_risk_and_unpracticed_subjects()** (12 connections) — `backend/tests/unit/domain/test_heuristic_analyzer.py`
- **.get_topic()** (11 connections) — `backend/src/tutoring/domain/entities/catalog.py`
- **.topics_for_subject()** (10 connections) — `backend/src/tutoring/domain/entities/catalog.py`
- **test_snapshot_raises_not_found_for_unknown_ids()** (10 connections) — `backend/tests/unit/domain/test_catalog_entities.py`
- **test_analyzer_with_no_sessions_returns_insufficient_data_and_empty_scores()** (10 connections) — `backend/tests/unit/domain/test_heuristic_analyzer.py`
- *... and 60 more nodes in this community*

## Relationships

- [Community 2](Community_2.md) (58 shared connections)
- [Community 0](Community_0.md) (42 shared connections)
- [Community 3](Community_3.md) (39 shared connections)
- [Community 4](Community_4.md) (27 shared connections)
- [Community 5](Community_5.md) (22 shared connections)
- [Community 15](Community_15.md) (18 shared connections)
- [Community 11](Community_11.md) (10 shared connections)
- [Community 10](Community_10.md) (8 shared connections)
- [Community 12](Community_12.md) (3 shared connections)
- [Community 19](Community_19.md) (3 shared connections)

## Source Files

- `backend/src/tutoring/domain/entities/__init__.py`
- `backend/src/tutoring/domain/entities/catalog.py`
- `backend/src/tutoring/domain/entities/student.py`
- `backend/src/tutoring/domain/validation.py`
- `backend/src/tutoring/domain/value_objects/exam_goal.py`
- `backend/src/tutoring/infrastructure/ml/sklearn_analyzer.py`
- `backend/src/tutoring/infrastructure/persistence/sqlite_catalog_repo.py`
- `backend/tests/integration/test_sklearn_analyzer.py`
- `backend/tests/integration/test_sqlite_catalog_repo.py`
- `backend/tests/integration/test_sqlite_session_repo.py`
- `backend/tests/unit/domain/test_attempt_value_objects.py`
- `backend/tests/unit/domain/test_catalog_entities.py`
- `backend/tests/unit/domain/test_heuristic_analyzer.py`

## Audit Trail

- EXTRACTED: 221 (47%)
- INFERRED: 245 (53%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*