# Community 4

> 51 nodes · cohesion 0.07

## Key Concepts

- **Student** (72 connections) — `backend/src/tutoring/domain/entities/student.py`
- **SqliteStudentRepository** (15 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_student_repo.py`
- **InMemoryStudentRepository** (14 connections) — `backend/src/tutoring/application/fakes.py`
- **test_sqlite_student_persistence_lifecycle()** (14 connections) — `backend/tests/integration/test_sqlite_student_repo.py`
- **._to_detail_dto()** (11 connections) — `backend/src/tutoring/application/use_cases/manage_students.py`
- **.upcoming_exams()** (10 connections) — `backend/src/tutoring/domain/entities/student.py`
- **init_sqlite_db()** (10 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_db.py`
- **.add_exam_goal()** (9 connections) — `backend/src/tutoring/domain/entities/student.py`
- **.save()** (9 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_student_repo.py`
- **test_in_memory_student_repository()** (9 connections) — `backend/tests/unit/application/test_fakes.py`
- **test_student_validates_profile_fields_and_updates()** (9 connections) — `backend/tests/unit/domain/test_student_entity.py`
- **test_student_rejects_blank_required_fields()** (7 connections) — `backend/tests/unit/domain/test_student_entity.py`
- **.save()** (6 connections) — `backend/src/tutoring/application/fakes.py`
- **.exam_goals()** (6 connections) — `backend/src/tutoring/domain/entities/student.py`
- **.rename()** (6 connections) — `backend/src/tutoring/domain/entities/student.py`
- **._hydrate_student()** (6 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_student_repo.py`
- **._append_unique_exam_goal()** (5 connections) — `backend/src/tutoring/domain/entities/student.py`
- **.__init__()** (5 connections) — `backend/src/tutoring/domain/entities/student.py`
- **.update_academic_level()** (5 connections) — `backend/src/tutoring/domain/entities/student.py`
- **.get_by_id()** (5 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_student_repo.py`
- **.get_by_id()** (4 connections) — `backend/src/tutoring/application/fakes.py`
- **.academic_level()** (4 connections) — `backend/src/tutoring/domain/entities/student.py`
- **.full_name()** (4 connections) — `backend/src/tutoring/domain/entities/student.py`
- **.pedagogical_notes()** (4 connections) — `backend/src/tutoring/domain/entities/student.py`
- **.list_all()** (4 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_student_repo.py`
- *... and 26 more nodes in this community*

## Relationships

- [Community 1](Community_1.md) (27 shared connections)
- [Community 0](Community_0.md) (26 shared connections)
- [Community 2](Community_2.md) (20 shared connections)
- [Community 5](Community_5.md) (13 shared connections)
- [Community 19](Community_19.md) (10 shared connections)
- [Community 11](Community_11.md) (8 shared connections)
- [Community 15](Community_15.md) (3 shared connections)
- [Community 10](Community_10.md) (2 shared connections)
- [Community 3](Community_3.md) (1 shared connections)
- [Community 12](Community_12.md) (1 shared connections)

## Source Files

- `backend/src/tutoring/application/fakes.py`
- `backend/src/tutoring/application/use_cases/manage_students.py`
- `backend/src/tutoring/domain/entities/student.py`
- `backend/src/tutoring/domain/ports/repositories.py`
- `backend/src/tutoring/infrastructure/persistence/sqlite_db.py`
- `backend/src/tutoring/infrastructure/persistence/sqlite_student_repo.py`
- `backend/tests/integration/test_sqlite_student_repo.py`
- `backend/tests/unit/application/test_fakes.py`
- `backend/tests/unit/domain/test_student_entity.py`

## Audit Trail

- EXTRACTED: 117 (57%)
- INFERRED: 88 (43%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*