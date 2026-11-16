"""Unit tests for T1.1: Enums, validation helper, and ExerciseAttempt value object."""

from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from tutoring.domain.enums import AttemptOutcome, ErrorCause, LearningTrend
from tutoring.domain.exceptions import InvalidAttemptError, ValidationError
from tutoring.domain.validation import require_non_empty
from tutoring.domain.value_objects.attempt import ExerciseAttempt


def test_require_non_empty_strips_valid_text() -> None:
    assert require_non_empty("  Álgebra lineal  ", "name") == "Álgebra lineal"


@pytest.mark.parametrize("raw", ["", "   ", "\n\t"])
def test_require_non_empty_rejects_blank_text(raw: str) -> None:
    with pytest.raises(ValidationError, match="name"):
        require_non_empty(raw, "name")


def test_attempt_outcome_failure_weights() -> None:
    assert AttemptOutcome.SUCCESS.failure_weight() == 0.0
    assert AttemptOutcome.PARTIAL.failure_weight() == 0.5
    assert AttemptOutcome.FAILURE.failure_weight() == 1.0


def test_enums_expose_expected_members() -> None:
    assert {c.value for c in ErrorCause} == {
        "CONCEPT",
        "CALCULATION",
        "COMPREHENSION",
        "CARELESSNESS",
    }
    assert {t.value for t in LearningTrend} == {
        "IMPROVING",
        "STAGNANT",
        "REGRESSING",
        "INSUFFICIENT_DATA",
    }


def test_successful_attempt_cannot_have_error_cause() -> None:
    with pytest.raises(InvalidAttemptError):
        ExerciseAttempt(
            exercise_type_id=uuid4(),
            outcome=AttemptOutcome.SUCCESS,
            error_cause=ErrorCause.CALCULATION,
        )


def test_successful_attempt_without_error_cause_is_valid_and_normalizes_notes() -> None:
    attempt = ExerciseAttempt(
        exercise_type_id=uuid4(),
        outcome=AttemptOutcome.SUCCESS,
        notes="  Resuelto sin ayuda  ",
    )

    assert attempt.error_cause is None
    assert attempt.notes == "Resuelto sin ayuda"
    assert attempt.severity_weight() == 0.0


def test_partial_and_failure_attempts_support_optional_or_specific_error_cause() -> None:
    partial_no_cause = ExerciseAttempt(
        exercise_type_id=uuid4(),
        outcome=AttemptOutcome.PARTIAL,
    )
    failure_with_cause = ExerciseAttempt(
        exercise_type_id=uuid4(),
        outcome=AttemptOutcome.FAILURE,
        error_cause=ErrorCause.CONCEPT,
    )

    assert partial_no_cause.severity_weight() == 0.5
    assert partial_no_cause.error_cause is None
    assert failure_with_cause.severity_weight() == 1.0
    assert failure_with_cause.error_cause == ErrorCause.CONCEPT


def test_exercise_attempt_is_immutable() -> None:
    attempt = ExerciseAttempt(
        exercise_type_id=uuid4(),
        outcome=AttemptOutcome.FAILURE,
        error_cause=ErrorCause.CARELESSNESS,
    )

    with pytest.raises(FrozenInstanceError):
        attempt.outcome = AttemptOutcome.SUCCESS  # type: ignore[misc]
