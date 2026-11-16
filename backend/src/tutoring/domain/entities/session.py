"""TutoringSession aggregate root entity."""

from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

from tutoring.domain.exceptions import ValidationError
from tutoring.domain.value_objects.attempt import ExerciseAttempt


def _validate_duration(duration_minutes: int) -> int:
    if duration_minutes <= 0:
        raise ValidationError("Session duration_minutes must be greater than zero.")
    return duration_minutes


class TutoringSession:
    """Aggregate root capturing a tutoring session and its exercise attempts."""

    def __init__(
        self,
        id: UUID,
        student_id: UUID,
        occurred_at: datetime,
        duration_minutes: int,
        session_notes: str = "",
        attempts: Sequence[ExerciseAttempt] = (),
    ) -> None:
        self._id = id
        self._student_id = student_id
        self._occurred_at = occurred_at
        self._duration_minutes = _validate_duration(duration_minutes)
        self._session_notes = session_notes.strip()
        self._attempts: list[ExerciseAttempt] = list(attempts)

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def student_id(self) -> UUID:
        return self._student_id

    @property
    def occurred_at(self) -> datetime:
        return self._occurred_at

    @property
    def duration_minutes(self) -> int:
        return self._duration_minutes

    @property
    def session_notes(self) -> str:
        return self._session_notes

    @property
    def attempts(self) -> tuple[ExerciseAttempt, ...]:
        return tuple(self._attempts)

    def record_attempt(self, attempt: ExerciseAttempt) -> None:
        """Append a validated exercise attempt to this session."""
        self._attempts.append(attempt)

    def failure_rate(self) -> float:
        """Compute weighted failure rate over recorded attempts in [0.0, 1.0]."""
        if not self._attempts:
            return 0.0
        total_weight = sum(attempt.severity_weight() for attempt in self._attempts)
        return total_weight / len(self._attempts)

    def update_notes(self, notes: str) -> None:
        """Update normalized session notes."""
        self._session_notes = notes.strip()

    def update_duration(self, duration_minutes: int) -> None:
        """Validate and update session duration in minutes."""
        self._duration_minutes = _validate_duration(duration_minutes)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TutoringSession):
            return NotImplemented
        return (
            self._id == other._id
            and self._student_id == other._student_id
            and self._occurred_at == other._occurred_at
            and self._duration_minutes == other._duration_minutes
            and self._session_notes == other._session_notes
            and self._attempts == other._attempts
        )

    def __repr__(self) -> str:
        return (
            f"TutoringSession(id={self._id!r}, student_id={self._student_id!r}, "
            f"occurred_at={self._occurred_at!r}, attempts={len(self._attempts)})"
        )
