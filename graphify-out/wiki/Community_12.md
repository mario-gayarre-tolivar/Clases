# Community 12

> 41 nodes · cohesion 0.10

## Key Concepts

- **TutoringSession** (65 connections) — `backend/src/tutoring/domain/entities/session.py`
- **fakes.py** (24 connections) — `backend/src/tutoring/application/fakes.py`
- **SqliteSessionRepository** (15 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_session_repo.py`
- **._to_dto()** (13 connections) — `backend/src/tutoring/application/use_cases/record_session.py`
- **InMemorySessionRepository** (11 connections) — `backend/src/tutoring/application/fakes.py`
- **.save()** (9 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_session_repo.py`
- **test_in_memory_session_repository()** (9 connections) — `backend/tests/unit/application/test_fakes.py`
- **test_session_normalizes_notes_and_exposes_immutable_attempts()** (9 connections) — `backend/tests/unit/domain/test_session_entity.py`
- **._hydrate_session()** (8 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_session_repo.py`
- **.id()** (7 connections) — `backend/src/tutoring/domain/entities/session.py`
- **.attempts()** (6 connections) — `backend/src/tutoring/domain/entities/session.py`
- **.failure_rate()** (5 connections) — `backend/src/tutoring/domain/entities/session.py`
- **.__init__()** (5 connections) — `backend/src/tutoring/domain/entities/session.py`
- **.update_duration()** (5 connections) — `backend/src/tutoring/domain/entities/session.py`
- **.get_by_id()** (5 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_session_repo.py`
- **.list_by_student()** (5 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_session_repo.py`
- **.get_by_id()** (4 connections) — `backend/src/tutoring/application/fakes.py`
- **.list_by_student()** (4 connections) — `backend/src/tutoring/application/fakes.py`
- **.save()** (4 connections) — `backend/src/tutoring/application/fakes.py`
- **UUID** (4 connections)
- **.duration_minutes()** (4 connections) — `backend/src/tutoring/domain/entities/session.py`
- **.occurred_at()** (4 connections) — `backend/src/tutoring/domain/entities/session.py`
- **.session_notes()** (4 connections) — `backend/src/tutoring/domain/entities/session.py`
- **.student_id()** (4 connections) — `backend/src/tutoring/domain/entities/session.py`
- **_validate_duration()** (4 connections) — `backend/src/tutoring/domain/entities/session.py`
- *... and 16 more nodes in this community*

## Relationships

- [Community 5](Community_5.md) (25 shared connections)
- [Community 8](Community_8.md) (17 shared connections)
- [Community 2](Community_2.md) (14 shared connections)
- [Community 13](Community_13.md) (10 shared connections)
- [Community 1](Community_1.md) (10 shared connections)
- [Community 24](Community_24.md) (10 shared connections)
- [Community 17](Community_17.md) (9 shared connections)
- [Community 4](Community_4.md) (5 shared connections)
- [Community 20](Community_20.md) (1 shared connections)
- [Community 28](Community_28.md) (1 shared connections)
- [Community 25](Community_25.md) (1 shared connections)

## Source Files

- `backend/src/tutoring/application/fakes.py`
- `backend/src/tutoring/application/use_cases/record_session.py`
- `backend/src/tutoring/domain/entities/session.py`
- `backend/src/tutoring/infrastructure/persistence/sqlite_session_repo.py`
- `backend/tests/unit/application/test_fakes.py`
- `backend/tests/unit/domain/test_session_entity.py`

## Audit Trail

- EXTRACTED: 117 (64%)
- INFERRED: 65 (36%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*