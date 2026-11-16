# Community 5

> 56 nodes · cohesion 0.08

## Key Concepts

- **AttemptOutcome** (41 connections) — `backend/src/tutoring/domain/enums.py`
- **ExerciseAttempt** (41 connections) — `backend/src/tutoring/domain/value_objects/attempt.py`
- **pytest** (41 connections)
- **ErrorCause** (39 connections) — `backend/src/tutoring/domain/enums.py`
- **enums.py** (22 connections) — `backend/src/tutoring/domain/enums.py`
- **attempt.py** (21 connections) — `backend/src/tutoring/domain/value_objects/attempt.py`
- **LearningTrend** (17 connections) — `backend/src/tutoring/domain/enums.py`
- **sqlite_session_repo.py** (17 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_session_repo.py`
- **diagnostic.py** (16 connections) — `backend/src/tutoring/domain/value_objects/diagnostic.py`
- **test_attempt_value_objects.py** (16 connections) — `backend/tests/unit/domain/test_attempt_value_objects.py`
- **test_sqlite_session_repo.py** (14 connections) — `backend/tests/integration/test_sqlite_session_repo.py`
- **test_fakes.py** (13 connections) — `backend/tests/unit/application/test_fakes.py`
- **SubjectPriority** (12 connections) — `backend/src/tutoring/domain/value_objects/diagnostic.py`
- **test_session_entity.py** (11 connections) — `backend/tests/unit/domain/test_session_entity.py`
- **value_objects/__init__.py** (10 connections) — `backend/src/tutoring/domain/value_objects/__init__.py`
- **WeakExerciseType** (9 connections) — `backend/src/tutoring/domain/value_objects/diagnostic.py`
- **test_session_failure_rate_for_empty_and_mixed_attempts()** (9 connections) — `backend/tests/unit/domain/test_session_entity.py`
- **ExamAlert** (8 connections) — `backend/src/tutoring/domain/value_objects/diagnostic.py`
- **test_recency_weight_and_weighted_failure_rate_prioritize_recent_errors()** (8 connections) — `backend/tests/unit/domain/test_heuristic_analyzer.py`
- **InvalidAttemptError** (7 connections) — `backend/src/tutoring/domain/exceptions.py`
- **test_successful_attempt_cannot_have_error_cause()** (6 connections) — `backend/tests/unit/domain/test_attempt_value_objects.py`
- **test_session_rejects_non_positive_duration()** (6 connections) — `backend/tests/unit/domain/test_session_entity.py`
- **test_exercise_attempt_is_immutable()** (5 connections) — `backend/tests/unit/domain/test_attempt_value_objects.py`
- **test_partial_and_failure_attempts_support_optional_or_specific_error_cause()** (5 connections) — `backend/tests/unit/domain/test_attempt_value_objects.py`
- **test_require_non_empty_rejects_blank_text()** (5 connections) — `backend/tests/unit/domain/test_attempt_value_objects.py`
- *... and 31 more nodes in this community*

## Relationships

- [Community 2](Community_2.md) (51 shared connections)
- [Community 4](Community_4.md) (37 shared connections)
- [Community 13](Community_13.md) (30 shared connections)
- [Community 12](Community_12.md) (25 shared connections)
- [Community 17](Community_17.md) (19 shared connections)
- [Community 1](Community_1.md) (12 shared connections)
- [Community 20](Community_20.md) (11 shared connections)
- [Community 8](Community_8.md) (11 shared connections)
- [Community 24](Community_24.md) (11 shared connections)
- [Community 25](Community_25.md) (9 shared connections)
- [Community 27](Community_27.md) (1 shared connections)

## Source Files

- `backend/src/tutoring/domain/entities/session.py`
- `backend/src/tutoring/domain/enums.py`
- `backend/src/tutoring/domain/exceptions.py`
- `backend/src/tutoring/domain/value_objects/__init__.py`
- `backend/src/tutoring/domain/value_objects/attempt.py`
- `backend/src/tutoring/domain/value_objects/diagnostic.py`
- `backend/src/tutoring/infrastructure/persistence/sqlite_session_repo.py`
- `backend/tests/integration/test_sqlite_session_repo.py`
- `backend/tests/unit/application/test_fakes.py`
- `backend/tests/unit/domain/test_attempt_value_objects.py`
- `backend/tests/unit/domain/test_heuristic_analyzer.py`
- `backend/tests/unit/domain/test_session_entity.py`

## Audit Trail

- EXTRACTED: 226 (68%)
- INFERRED: 107 (32%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*