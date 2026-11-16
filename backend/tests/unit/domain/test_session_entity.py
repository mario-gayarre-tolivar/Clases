"""Unit tests for T1.4: TutoringSession aggregate root."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from tutoring.domain.entities.session import TutoringSession
from tutoring.domain.enums import AttemptOutcome, ErrorCause
from tutoring.domain.exceptions import ValidationError
from tutoring.domain.value_objects.attempt import ExerciseAttempt


def test_session_normalizes_notes_and_exposes_immutable_attempts() -> None:
    attempt = ExerciseAttempt(
        exercise_type_id=uuid4(),
        outcome=AttemptOutcome.SUCCESS,
    )
    session = TutoringSession(
        id=uuid4(),
        student_id=uuid4(),
        occurred_at=datetime(2026, 11, 16, 17, 0, tzinfo=timezone.utc),
        duration_minutes=60,
        session_notes="  Repaso de integrales  ",
        attempts=[attempt],
    )

    assert session.duration_minutes == 60
    assert session.session_notes == "Repaso de integrales"
    assert session.attempts == (attempt,)

    session.update_notes("  Añadir ejercicios de partes  ")
    session.update_duration(90)
    assert session.session_notes == "Añadir ejercicios de partes"
    assert session.duration_minutes == 90


@pytest.mark.parametrize("duration", [0, -15])
def test_session_rejects_non_positive_duration(duration: int) -> None:
    with pytest.raises(ValidationError):
        TutoringSession(
            id=uuid4(),
            student_id=uuid4(),
            occurred_at=datetime(2026, 11, 16, 17, 0, tzinfo=timezone.utc),
            duration_minutes=duration,
        )

    session = TutoringSession(
        id=uuid4(),
        student_id=uuid4(),
        occurred_at=datetime(2026, 11, 16, 17, 0, tzinfo=timezone.utc),
        duration_minutes=60,
    )
    with pytest.raises(ValidationError):
        session.update_duration(duration)


def test_session_failure_rate_for_empty_and_mixed_attempts() -> None:
    session = TutoringSession(
        id=uuid4(),
        student_id=uuid4(),
        occurred_at=datetime(2026, 11, 16, 17, 0, tzinfo=timezone.utc),
        duration_minutes=60,
    )
    assert session.failure_rate() == 0.0

    session.record_attempt(
        ExerciseAttempt(exercise_type_id=uuid4(), outcome=AttemptOutcome.SUCCESS)
    )
    session.record_attempt(
        ExerciseAttempt(
            exercise_type_id=uuid4(),
            outcome=AttemptOutcome.PARTIAL,
            error_cause=ErrorCause.CALCULATION,
        )
    )
    session.record_attempt(
        ExerciseAttempt(
            exercise_type_id=uuid4(),
            outcome=AttemptOutcome.FAILURE,
            error_cause=ErrorCause.CONCEPT,
        )
    )

    # (0.0 + 0.5 + 1.0) / 3 = 0.5
    assert session.failure_rate() == pytest.approx(0.5)
    assert len(session.attempts) == 3
