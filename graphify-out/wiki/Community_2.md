# Community 2

> 59 nodes · cohesion 0.07

## Key Concepts

- **heuristic_analyzer.py** (35 connections) — `backend/src/tutoring/domain/analytics/heuristic_analyzer.py`
- **feature_extractor.py** (30 connections) — `backend/src/tutoring/domain/analytics/feature_extractor.py`
- **scoring.py** (27 connections) — `backend/src/tutoring/domain/analytics/scoring.py`
- **session.py** (26 connections) — `backend/src/tutoring/domain/entities/session.py`
- **TimedAttempt** (22 connections) — `backend/src/tutoring/domain/analytics/scoring.py`
- **FeatureExtractor** (20 connections) — `backend/src/tutoring/domain/analytics/feature_extractor.py`
- **test_feature_extractor.py** (16 connections) — `backend/tests/unit/domain/test_feature_extractor.py`
- **test_feature_extractor_extracts_student_and_subject_vectors()** (16 connections) — `backend/tests/unit/domain/test_feature_extractor.py`
- **.extract_subject_features()** (14 connections) — `backend/src/tutoring/domain/analytics/feature_extractor.py`
- **collections_abc** (12 connections)
- **.extract_student_features()** (11 connections) — `backend/src/tutoring/domain/analytics/feature_extractor.py`
- **collect_timed_attempts()** (11 connections) — `backend/src/tutoring/domain/analytics/scoring.py`
- **._build_feature_vector()** (10 connections) — `backend/src/tutoring/domain/analytics/feature_extractor.py`
- **FeatureVector** (10 connections) — `backend/src/tutoring/domain/analytics/feature_extractor.py`
- **compute_weighted_failure_rate()** (10 connections) — `backend/src/tutoring/domain/analytics/scoring.py`
- **compute_learning_trend()** (9 connections) — `backend/src/tutoring/domain/analytics/scoring.py`
- **compute_dominant_error_cause()** (8 connections) — `backend/src/tutoring/domain/analytics/scoring.py`
- **compute_recency_weight()** (8 connections) — `backend/src/tutoring/domain/analytics/scoring.py`
- **test_compute_learning_trend_covers_all_classifications()** (8 connections) — `backend/tests/unit/domain/test_heuristic_analyzer.py`
- **dataclasses** (8 connections)
- **validate_analytics_params()** (7 connections) — `backend/src/tutoring/domain/analytics/scoring.py`
- **test_dominant_error_cause_uses_recency_and_severity_weights()** (7 connections) — `backend/tests/unit/domain/test_heuristic_analyzer.py`
- **analytics/__init__.py** (6 connections) — `backend/src/tutoring/domain/analytics/__init__.py`
- **compute_failure_delta()** (6 connections) — `backend/src/tutoring/domain/analytics/scoring.py`
- **test_feature_extractor_handles_empty_student_cleanly()** (6 connections) — `backend/tests/unit/domain/test_feature_extractor.py`
- *... and 34 more nodes in this community*

## Relationships

- [Community 5](Community_5.md) (51 shared connections)
- [Community 13](Community_13.md) (37 shared connections)
- [Community 4](Community_4.md) (32 shared connections)
- [Community 17](Community_17.md) (16 shared connections)
- [Community 12](Community_12.md) (14 shared connections)
- [Community 1](Community_1.md) (5 shared connections)
- [Community 8](Community_8.md) (3 shared connections)
- [Community 25](Community_25.md) (1 shared connections)
- [Community 20](Community_20.md) (1 shared connections)

## Source Files

- `backend/src/tutoring/domain/analytics/__init__.py`
- `backend/src/tutoring/domain/analytics/feature_extractor.py`
- `backend/src/tutoring/domain/analytics/heuristic_analyzer.py`
- `backend/src/tutoring/domain/analytics/scoring.py`
- `backend/src/tutoring/domain/entities/session.py`
- `backend/tests/unit/domain/test_feature_extractor.py`
- `backend/tests/unit/domain/test_heuristic_analyzer.py`

## Audit Trail

- EXTRACTED: 232 (82%)
- INFERRED: 50 (18%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*