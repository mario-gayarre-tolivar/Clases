# Community 43

> 11 nodes · cohesion 0.29

## Key Concepts

- **SqliteStudentRepository** (15 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_student_repo.py`
- **test_sqlite_student_persistence_lifecycle()** (14 connections) — `backend/tests/integration/test_sqlite_student_repo.py`
- **._hydrate_student()** (6 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_student_repo.py`
- **.get_by_id()** (5 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_student_repo.py`
- **.list_all()** (4 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_student_repo.py`
- **UUID** (3 connections)
- **.delete()** (3 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_student_repo.py`
- **.__init__()** (2 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_student_repo.py`
- **Connection** (1 connections)
- **Row** (1 connections)
- **Persists and loads Student aggregates including ExamGoal value objects.** (1 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_student_repo.py`

## Relationships

- [Community 13](Community_13.md) (8 shared connections)
- [Community 4](Community_4.md) (7 shared connections)
- [Community 1](Community_1.md) (4 shared connections)
- [Community 25](Community_25.md) (2 shared connections)
- [Community 28](Community_28.md) (1 shared connections)
- [Community 8](Community_8.md) (1 shared connections)

## Source Files

- `backend/src/tutoring/infrastructure/persistence/sqlite_student_repo.py`
- `backend/tests/integration/test_sqlite_student_repo.py`

## Audit Trail

- EXTRACTED: 24 (62%)
- INFERRED: 15 (38%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*