# Community 25

> 24 nodes · cohesion 0.11

## Key Concepts

- **app.py** (63 connections) — `backend/src/tutoring/presentation/api/app.py`
- **init_sqlite_db()** (10 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_db.py`
- **DomainError** (8 connections) — `backend/src/tutoring/domain/exceptions.py`
- **sqlite_db.py** (8 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_db.py`
- **BaseModel** (7 connections)
- **sqlite3** (5 connections)
- **ExerciseAttemptPayload** (4 connections) — `backend/src/tutoring/presentation/api/app.py`
- **CreateExamGoalPayload** (2 connections) — `backend/src/tutoring/presentation/api/app.py`
- **CreateExerciseTypePayload** (2 connections) — `backend/src/tutoring/presentation/api/app.py`
- **CreateStudentPayload** (2 connections) — `backend/src/tutoring/presentation/api/app.py`
- **CreateSubjectPayload** (2 connections) — `backend/src/tutoring/presentation/api/app.py`
- **CreateTopicPayload** (2 connections) — `backend/src/tutoring/presentation/api/app.py`
- **RecordSessionPayload** (2 connections) — `backend/src/tutoring/presentation/api/app.py`
- **pathlib** (2 connections)
- **Base exception for all domain-level errors.** (1 connections) — `backend/src/tutoring/domain/exceptions.py`
- **Connection** (1 connections)
- **SQLite database connection and schema initialization.** (1 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_db.py`
- **Create SQLite database connection and initialize tables.** (1 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_db.py`
- **FastAPI application factory, dependency wiring, and domain error handlers.** (1 connections) — `backend/src/tutoring/presentation/api/app.py`
- **Exception** (1 connections)
- **fastapi_middleware_cors** (1 connections)
- **fastapi_responses** (1 connections)
- **Path** (1 connections)
- **pydantic** (1 connections)

## Relationships

- [Community 4](Community_4.md) (12 shared connections)
- [Community 20](Community_20.md) (12 shared connections)
- [Community 27](Community_27.md) (9 shared connections)
- [Community 5](Community_5.md) (9 shared connections)
- [Community 1](Community_1.md) (6 shared connections)
- [Community 8](Community_8.md) (6 shared connections)
- [Community 28](Community_28.md) (3 shared connections)
- [Community 43](Community_43.md) (2 shared connections)
- [Community 24](Community_24.md) (2 shared connections)
- [Community 44](Community_44.md) (2 shared connections)
- [Community 13](Community_13.md) (1 shared connections)
- [Community 12](Community_12.md) (1 shared connections)

## Source Files

- `backend/src/tutoring/domain/exceptions.py`
- `backend/src/tutoring/infrastructure/persistence/sqlite_db.py`
- `backend/src/tutoring/presentation/api/app.py`

## Audit Trail

- EXTRACTED: 96 (98%)
- INFERRED: 2 (2%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*