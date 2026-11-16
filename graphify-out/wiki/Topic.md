# Topic

> God node · 47 connections · `backend/src/tutoring/domain/entities/catalog.py`

**Community:** [Community 1](Community_1.md)

## Connections by Relation

### calls
- .create_topic() `EXTRACTED`
- .get_snapshot() `EXTRACTED`

### contains
- catalog.py `EXTRACTED`

### imports
- repositories.py `EXTRACTED`
- fakes.py `EXTRACTED`
- manage_catalog.py `EXTRACTED`
- sqlite_catalog_repo.py `EXTRACTED`
- entities/__init__.py `EXTRACTED`

### method
- .rename() `EXTRACTED`
- .__post_init__() `EXTRACTED`

### rationale_for
- Subject topic representing the second level of the catalog hierarchy. `EXTRACTED`

### references
- .resolve_exercise_path() `EXTRACTED`
- .get_topic() `EXTRACTED`
- .topics_for_subject() `EXTRACTED`
- .__init__() `EXTRACTED`
- .save_topic() `EXTRACTED`
- .all_topics() `EXTRACTED`
- .save_topic() `EXTRACTED`
- .get_topic() `EXTRACTED`
- .get_topic() `EXTRACTED`
- .save_topic() `EXTRACTED`
- .get_topic() `EXTRACTED`

### uses
- CatalogRepository `INFERRED`
- ManageCatalogUseCase `INFERRED`
- test_generate_student_diagnostic_orchestration() `INFERRED`
- InMemoryCatalogRepository `INFERRED`
- test_sqlite_session_persistence_lifecycle() `INFERRED`
- test_record_session_validates_student_and_exercise_types_and_saves() `INFERRED`
- SqliteCatalogRepository `INFERRED`
- test_sqlite_catalog_persistence_and_snapshot() `INFERRED`
- test_feature_extractor_extracts_student_and_subject_vectors() `INFERRED`
- test_sklearn_analyzer_trained_inference() `INFERRED`
- test_sklearn_analyzer_fallback_when_untrained() `INFERRED`
- test_in_memory_catalog_repository() `INFERRED`
- test_snapshot_resolves_hierarchy_and_listings() `INFERRED`
- test_analyzer_identifies_weak_exercise_types_excluding_mastered_ones() `INFERRED`
- test_analyzer_propagates_subject_and_overall_trends_with_regression_bonus() `INFERRED`
- test_subject_priority_ranking_combines_failure_rate_and_exam_urgency() `INFERRED`
- test_analyzer_subject_weighted_failure_rate_reflects_recency() `INFERRED`
- test_exam_alerts_capture_readiness_risk_and_unpracticed_subjects() `INFERRED`
- test_analyzer_with_no_sessions_returns_insufficient_data_and_empty_scores() `INFERRED`
- test_catalog_entities_normalize_and_validate_names() `INFERRED`
- *…and 5 more `uses` connection(s) not listed (lowest-degree first to go)*

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*