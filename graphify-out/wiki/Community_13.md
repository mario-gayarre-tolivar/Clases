# Community 13

> 41 nodes · cohesion 0.12

## Key Concepts

- **Student** (72 connections) — `backend/src/tutoring/domain/entities/student.py`
- **AcademicCatalogSnapshot** (53 connections) — `backend/src/tutoring/domain/entities/catalog.py`
- **HeuristicPedagogicalAnalyzer** (33 connections) — `backend/src/tutoring/domain/analytics/heuristic_analyzer.py`
- **test_heuristic_analyzer.py** (23 connections) — `backend/tests/unit/domain/test_heuristic_analyzer.py`
- **.id()** (20 connections) — `backend/src/tutoring/domain/entities/student.py`
- **.analyze()** (17 connections) — `backend/src/tutoring/domain/analytics/heuristic_analyzer.py`
- **test_analyzer_identifies_weak_exercise_types_excluding_mastered_ones()** (13 connections) — `backend/tests/unit/domain/test_heuristic_analyzer.py`
- **test_analyzer_propagates_subject_and_overall_trends_with_regression_bonus()** (13 connections) — `backend/tests/unit/domain/test_heuristic_analyzer.py`
- **test_subject_priority_ranking_combines_failure_rate_and_exam_urgency()** (13 connections) — `backend/tests/unit/domain/test_heuristic_analyzer.py`
- **._build_subject_priorities()** (12 connections) — `backend/src/tutoring/domain/analytics/heuristic_analyzer.py`
- **test_analyzer_subject_weighted_failure_rate_reflects_recency()** (12 connections) — `backend/tests/unit/domain/test_heuristic_analyzer.py`
- **test_exam_alerts_capture_readiness_risk_and_unpracticed_subjects()** (12 connections) — `backend/tests/unit/domain/test_heuristic_analyzer.py`
- **._build_exam_alerts()** (11 connections) — `backend/src/tutoring/domain/analytics/heuristic_analyzer.py`
- **test_analyzer_with_no_sessions_returns_insufficient_data_and_empty_scores()** (10 connections) — `backend/tests/unit/domain/test_heuristic_analyzer.py`
- **entities/__init__.py** (9 connections) — `backend/src/tutoring/domain/entities/__init__.py`
- **.save()** (9 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_student_repo.py`
- **test_student_validates_profile_fields_and_updates()** (9 connections) — `backend/tests/unit/domain/test_student_entity.py`
- **._build_weak_exercise_types()** (8 connections) — `backend/src/tutoring/domain/analytics/heuristic_analyzer.py`
- **test_student_rejects_blank_required_fields()** (7 connections) — `backend/tests/unit/domain/test_student_entity.py`
- **._group_attempts_by_subject()** (6 connections) — `backend/src/tutoring/domain/analytics/heuristic_analyzer.py`
- **.exam_goals()** (6 connections) — `backend/src/tutoring/domain/entities/student.py`
- **.rename()** (6 connections) — `backend/src/tutoring/domain/entities/student.py`
- **UUID** (5 connections)
- **.update_academic_level()** (5 connections) — `backend/src/tutoring/domain/entities/student.py`
- **._group_exams_by_subject()** (4 connections) — `backend/src/tutoring/domain/analytics/heuristic_analyzer.py`
- *... and 16 more nodes in this community*

## Relationships

- [Community 1](Community_1.md) (45 shared connections)
- [Community 2](Community_2.md) (37 shared connections)
- [Community 4](Community_4.md) (33 shared connections)
- [Community 5](Community_5.md) (30 shared connections)
- [Community 17](Community_17.md) (26 shared connections)
- [Community 24](Community_24.md) (15 shared connections)
- [Community 27](Community_27.md) (12 shared connections)
- [Community 12](Community_12.md) (10 shared connections)
- [Community 43](Community_43.md) (8 shared connections)
- [Community 8](Community_8.md) (5 shared connections)
- [Community 20](Community_20.md) (3 shared connections)
- [Community 28](Community_28.md) (1 shared connections)

## Source Files

- `backend/src/tutoring/domain/analytics/heuristic_analyzer.py`
- `backend/src/tutoring/domain/entities/__init__.py`
- `backend/src/tutoring/domain/entities/catalog.py`
- `backend/src/tutoring/domain/entities/student.py`
- `backend/src/tutoring/infrastructure/persistence/sqlite_student_repo.py`
- `backend/tests/unit/domain/test_heuristic_analyzer.py`
- `backend/tests/unit/domain/test_student_entity.py`

## Audit Trail

- EXTRACTED: 165 (51%)
- INFERRED: 158 (49%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*