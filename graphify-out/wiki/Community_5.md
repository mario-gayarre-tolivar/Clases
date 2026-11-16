# Community 5

> 49 nodes · cohesion 0.08

## Key Concepts

- **CatalogRepository** (31 connections) — `backend/src/tutoring/domain/ports/repositories.py`
- **repositories.py** (25 connections) — `backend/src/tutoring/domain/ports/repositories.py`
- **StudentRepository** (22 connections) — `backend/src/tutoring/domain/ports/repositories.py`
- **sklearn_analyzer.py** (21 connections) — `backend/src/tutoring/infrastructure/ml/sklearn_analyzer.py`
- **SessionRepository** (18 connections) — `backend/src/tutoring/domain/ports/repositories.py`
- **sqlite_session_repo.py** (17 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_session_repo.py`
- **generate_diagnostic.py** (16 connections) — `backend/src/tutoring/application/use_cases/generate_diagnostic.py`
- **analyzer.py** (16 connections) — `backend/src/tutoring/domain/ports/analyzer.py`
- **sqlite_student_repo.py** (15 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_student_repo.py`
- **PedagogicalAnalyzerPort** (14 connections) — `backend/src/tutoring/domain/ports/analyzer.py`
- **GenerateStudentDiagnosticUseCase** (13 connections) — `backend/src/tutoring/application/use_cases/generate_diagnostic.py`
- **collections_abc** (12 connections)
- **.execute()** (10 connections) — `backend/src/tutoring/application/use_cases/generate_diagnostic.py`
- **.analyze()** (8 connections) — `backend/src/tutoring/domain/ports/analyzer.py`
- **UUID** (8 connections)
- **ports/__init__.py** (7 connections) — `backend/src/tutoring/domain/ports/__init__.py`
- **.__init__()** (5 connections) — `backend/src/tutoring/application/use_cases/generate_diagnostic.py`
- **.list_by_student()** (5 connections) — `backend/src/tutoring/domain/ports/repositories.py`
- **sqlite3** (5 connections)
- **typing** (5 connections)
- **.__init__()** (4 connections) — `backend/src/tutoring/application/use_cases/record_session.py`
- **.get_subject()** (4 connections) — `backend/src/tutoring/domain/ports/repositories.py`
- **.__init__()** (3 connections) — `backend/src/tutoring/application/use_cases/manage_students.py`
- **.get_exercise_type()** (3 connections) — `backend/src/tutoring/domain/ports/repositories.py`
- **.get_topic()** (3 connections) — `backend/src/tutoring/domain/ports/repositories.py`
- *... and 24 more nodes in this community*

## Relationships

- [Community 0](Community_0.md) (42 shared connections)
- [Community 2](Community_2.md) (36 shared connections)
- [Community 1](Community_1.md) (22 shared connections)
- [Community 3](Community_3.md) (16 shared connections)
- [Community 4](Community_4.md) (13 shared connections)
- [Community 10](Community_10.md) (12 shared connections)
- [Community 11](Community_11.md) (3 shared connections)
- [Community 12](Community_12.md) (3 shared connections)
- [Community 15](Community_15.md) (1 shared connections)
- [Community 19](Community_19.md) (1 shared connections)

## Source Files

- `backend/src/tutoring/application/use_cases/generate_diagnostic.py`
- `backend/src/tutoring/application/use_cases/manage_catalog.py`
- `backend/src/tutoring/application/use_cases/manage_students.py`
- `backend/src/tutoring/application/use_cases/record_session.py`
- `backend/src/tutoring/domain/ports/__init__.py`
- `backend/src/tutoring/domain/ports/analyzer.py`
- `backend/src/tutoring/domain/ports/repositories.py`
- `backend/src/tutoring/infrastructure/ml/sklearn_analyzer.py`
- `backend/src/tutoring/infrastructure/persistence/sqlite_session_repo.py`
- `backend/src/tutoring/infrastructure/persistence/sqlite_student_repo.py`

## Audit Trail

- EXTRACTED: 205 (86%)
- INFERRED: 33 (14%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*