# Community 4

> 57 nodes · cohesion 0.07

## Key Concepts

- **ExamGoal** (36 connections) — `backend/src/tutoring/domain/value_objects/exam_goal.py`
- **student.py** (30 connections) — `backend/src/tutoring/domain/entities/student.py`
- **ValidationError** (30 connections) — `backend/src/tutoring/domain/exceptions.py`
- **exceptions.py** (29 connections) — `backend/src/tutoring/domain/exceptions.py`
- **datetime** (26 connections)
- **uuid** (24 connections)
- **exam_goal.py** (19 connections) — `backend/src/tutoring/domain/value_objects/exam_goal.py`
- **require_non_empty()** (18 connections) — `backend/src/tutoring/domain/validation.py`
- **sqlite_student_repo.py** (15 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_student_repo.py`
- **test_generate_diagnostic.py** (14 connections) — `backend/tests/unit/application/test_generate_diagnostic.py`
- **test_student_entity.py** (13 connections) — `backend/tests/unit/domain/test_student_entity.py`
- **test_record_session.py** (12 connections) — `backend/tests/unit/application/test_record_session.py`
- **test_sqlite_student_repo.py** (11 connections) — `backend/tests/integration/test_sqlite_student_repo.py`
- **test_manage_students.py** (11 connections) — `backend/tests/unit/application/test_manage_students.py`
- **.upcoming_exams()** (10 connections) — `backend/src/tutoring/domain/entities/student.py`
- **.add_exam_goal()** (9 connections) — `backend/src/tutoring/domain/entities/student.py`
- **validation.py** (8 connections) — `backend/src/tutoring/domain/validation.py`
- **test_student_add_exam_goal_validates_past_date_and_duplicates()** (8 connections) — `backend/tests/unit/domain/test_student_entity.py`
- **.is_upcoming()** (7 connections) — `backend/src/tutoring/domain/value_objects/exam_goal.py`
- **test_sessions_and_diagnostic_api.py** (7 connections) — `backend/tests/integration/test_sessions_and_diagnostic_api.py`
- **test_students_api.py** (7 connections) — `backend/tests/integration/test_students_api.py`
- **test_catalog_api.py** (6 connections) — `backend/tests/integration/test_catalog_api.py`
- **._append_unique_exam_goal()** (5 connections) — `backend/src/tutoring/domain/entities/student.py`
- **.__init__()** (5 connections) — `backend/src/tutoring/domain/entities/student.py`
- **.days_remaining()** (5 connections) — `backend/src/tutoring/domain/value_objects/exam_goal.py`
- *... and 32 more nodes in this community*

## Relationships

- [Community 5](Community_5.md) (37 shared connections)
- [Community 13](Community_13.md) (33 shared connections)
- [Community 2](Community_2.md) (32 shared connections)
- [Community 17](Community_17.md) (14 shared connections)
- [Community 20](Community_20.md) (13 shared connections)
- [Community 1](Community_1.md) (12 shared connections)
- [Community 27](Community_27.md) (12 shared connections)
- [Community 25](Community_25.md) (12 shared connections)
- [Community 8](Community_8.md) (9 shared connections)
- [Community 43](Community_43.md) (7 shared connections)
- [Community 12](Community_12.md) (5 shared connections)
- [Community 28](Community_28.md) (4 shared connections)

## Source Files

- `backend/src/tutoring/domain/entities/catalog.py`
- `backend/src/tutoring/domain/entities/student.py`
- `backend/src/tutoring/domain/exceptions.py`
- `backend/src/tutoring/domain/validation.py`
- `backend/src/tutoring/domain/value_objects/exam_goal.py`
- `backend/src/tutoring/infrastructure/persistence/sqlite_student_repo.py`
- `backend/tests/integration/test_catalog_api.py`
- `backend/tests/integration/test_sessions_and_diagnostic_api.py`
- `backend/tests/integration/test_sqlite_student_repo.py`
- `backend/tests/integration/test_students_api.py`
- `backend/tests/unit/application/test_generate_diagnostic.py`
- `backend/tests/unit/application/test_manage_students.py`
- `backend/tests/unit/application/test_record_session.py`
- `backend/tests/unit/domain/test_attempt_value_objects.py`
- `backend/tests/unit/domain/test_student_entity.py`

## Audit Trail

- EXTRACTED: 264 (87%)
- INFERRED: 41 (13%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*