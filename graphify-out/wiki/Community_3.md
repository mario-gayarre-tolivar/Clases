# Community 3

> 66 nodes · cohesion 0.07

## Key Concepts

- **TutoringSession** (65 connections) — `backend/src/tutoring/domain/entities/session.py`
- **AttemptOutcome** (41 connections) — `backend/src/tutoring/domain/enums.py`
- **ExerciseAttempt** (41 connections) — `backend/src/tutoring/domain/value_objects/attempt.py`
- **ErrorCause** (39 connections) — `backend/src/tutoring/domain/enums.py`
- **test_attempt_value_objects.py** (16 connections) — `backend/tests/unit/domain/test_attempt_value_objects.py`
- **SqliteSessionRepository** (15 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_session_repo.py`
- **._to_dto()** (13 connections) — `backend/src/tutoring/application/use_cases/record_session.py`
- **InMemorySessionRepository** (11 connections) — `backend/src/tutoring/application/fakes.py`
- **.save()** (9 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_session_repo.py`
- **test_in_memory_session_repository()** (9 connections) — `backend/tests/unit/application/test_fakes.py`
- **test_session_failure_rate_for_empty_and_mixed_attempts()** (9 connections) — `backend/tests/unit/domain/test_session_entity.py`
- **test_session_normalizes_notes_and_exposes_immutable_attempts()** (9 connections) — `backend/tests/unit/domain/test_session_entity.py`
- **._hydrate_session()** (8 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_session_repo.py`
- **test_recency_weight_and_weighted_failure_rate_prioritize_recent_errors()** (8 connections) — `backend/tests/unit/domain/test_heuristic_analyzer.py`
- **.id()** (7 connections) — `backend/src/tutoring/domain/entities/session.py`
- **InvalidAttemptError** (7 connections) — `backend/src/tutoring/domain/exceptions.py`
- **test_dominant_error_cause_uses_recency_and_severity_weights()** (7 connections) — `backend/tests/unit/domain/test_heuristic_analyzer.py`
- **.attempts()** (6 connections) — `backend/src/tutoring/domain/entities/session.py`
- **test_successful_attempt_cannot_have_error_cause()** (6 connections) — `backend/tests/unit/domain/test_attempt_value_objects.py`
- **.failure_rate()** (5 connections) — `backend/src/tutoring/domain/entities/session.py`
- **.__init__()** (5 connections) — `backend/src/tutoring/domain/entities/session.py`
- **.update_duration()** (5 connections) — `backend/src/tutoring/domain/entities/session.py`
- **.get_by_id()** (5 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_session_repo.py`
- **.list_by_student()** (5 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_session_repo.py`
- **test_exercise_attempt_is_immutable()** (5 connections) — `backend/tests/unit/domain/test_attempt_value_objects.py`
- *... and 41 more nodes in this community*

## Relationships

- [Community 1](Community_1.md) (39 shared connections)
- [Community 2](Community_2.md) (36 shared connections)
- [Community 0](Community_0.md) (31 shared connections)
- [Community 12](Community_12.md) (18 shared connections)
- [Community 5](Community_5.md) (16 shared connections)
- [Community 11](Community_11.md) (13 shared connections)
- [Community 10](Community_10.md) (6 shared connections)
- [Community 15](Community_15.md) (3 shared connections)
- [Community 20](Community_20.md) (3 shared connections)
- [Community 4](Community_4.md) (1 shared connections)

## Source Files

- `backend/src/tutoring/application/fakes.py`
- `backend/src/tutoring/application/use_cases/record_session.py`
- `backend/src/tutoring/domain/entities/session.py`
- `backend/src/tutoring/domain/enums.py`
- `backend/src/tutoring/domain/exceptions.py`
- `backend/src/tutoring/domain/value_objects/attempt.py`
- `backend/src/tutoring/infrastructure/persistence/sqlite_session_repo.py`
- `backend/tests/unit/application/test_fakes.py`
- `backend/tests/unit/domain/test_attempt_value_objects.py`
- `backend/tests/unit/domain/test_heuristic_analyzer.py`
- `backend/tests/unit/domain/test_session_entity.py`

## Audit Trail

- EXTRACTED: 167 (54%)
- INFERRED: 143 (46%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*