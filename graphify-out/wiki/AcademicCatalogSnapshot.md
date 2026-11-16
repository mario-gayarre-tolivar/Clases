# AcademicCatalogSnapshot

> God node · 53 connections · `backend/src/tutoring/domain/entities/catalog.py`

**Community:** [Community 1](Community_1.md)

## Connections by Relation

### contains
- catalog.py `EXTRACTED`

### imports
- heuristic_analyzer.py `EXTRACTED`
- feature_extractor.py `EXTRACTED`
- repositories.py `EXTRACTED`
- fakes.py `EXTRACTED`
- sklearn_analyzer.py `EXTRACTED`
- analyzer.py `EXTRACTED`
- sqlite_catalog_repo.py `EXTRACTED`
- entities/__init__.py `EXTRACTED`

### method
- .get_subject() `EXTRACTED`
- .resolve_exercise_path() `EXTRACTED`
- .get_topic() `EXTRACTED`
- .topics_for_subject() `EXTRACTED`
- .get_exercise_type() `EXTRACTED`
- .exercise_types_for_topic() `EXTRACTED`
- .__init__() `EXTRACTED`
- .all_subjects() `EXTRACTED`
- .all_topics() `EXTRACTED`
- .all_exercise_types() `EXTRACTED`

### rationale_for
- Consistent, read-only hierarchical view over subjects, topics, and exercise… `EXTRACTED`

### references
- .analyze() `EXTRACTED`
- .extract_subject_features() `EXTRACTED`
- ._build_subject_priorities() `EXTRACTED`
- ._build_exam_alerts() `EXTRACTED`
- .analyze() `EXTRACTED`
- ._build_weak_exercise_types() `EXTRACTED`
- .analyze() `EXTRACTED`
- .get_snapshot() `EXTRACTED`
- ._group_attempts_by_subject() `EXTRACTED`
- .get_snapshot() `EXTRACTED`
- .get_snapshot() `EXTRACTED`

### uses
- HeuristicPedagogicalAnalyzer `INFERRED`
- CatalogRepository `INFERRED`
- EntityNotFoundError `INFERRED`
- InMemoryCatalogRepository `INFERRED`
- FeatureExtractor `INFERRED`
- SqliteCatalogRepository `INFERRED`
- SklearnPedagogicalAnalyzer `INFERRED`
- test_feature_extractor_extracts_student_and_subject_vectors() `INFERRED`
- test_sklearn_analyzer_trained_inference() `INFERRED`
- PedagogicalAnalyzerPort `INFERRED`
- test_sklearn_analyzer_fallback_when_untrained() `INFERRED`
- test_snapshot_resolves_hierarchy_and_listings() `INFERRED`
- test_analyzer_identifies_weak_exercise_types_excluding_mastered_ones() `INFERRED`
- test_analyzer_propagates_subject_and_overall_trends_with_regression_bonus() `INFERRED`
- test_subject_priority_ranking_combines_failure_rate_and_exam_urgency() `INFERRED`
- test_analyzer_subject_weighted_failure_rate_reflects_recency() `INFERRED`
- test_exam_alerts_capture_readiness_risk_and_unpracticed_subjects() `INFERRED`
- test_snapshot_raises_not_found_for_unknown_ids() `INFERRED`
- test_analyzer_with_no_sessions_returns_insufficient_data_and_empty_scores() `INFERRED`
- test_snapshot_rejects_duplicate_ids_and_logical_duplicate_names() `INFERRED`
- *…and 2 more `uses` connection(s) not listed (lowest-degree first to go)*

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*