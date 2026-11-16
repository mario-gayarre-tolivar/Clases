"""Value object representing a single evaluated exercise attempt."""

from dataclasses import dataclass
from uuid import UUID

from tutoring.domain.enums import AttemptOutcome, ErrorCause
from tutoring.domain.exceptions import InvalidAttemptError


@dataclass(frozen=True)
class ExerciseAttempt:
    """Immutable record of a student's attempt on a specific exercise type."""

    exercise_type_id: UUID
    outcome: AttemptOutcome
    error_cause: ErrorCause | None = None
    notes: str = ""

    def __post_init__(self) -> None:
        if self.outcome == AttemptOutcome.SUCCESS and self.error_cause is not None:
            raise InvalidAttemptError(
                "A successful exercise attempt cannot carry an error cause."
            )
        object.__setattr__(self, "notes", self.notes.strip())

    def severity_weight(self) -> float:
        """Return the failure severity weight corresponding to the attempt outcome."""
        return self.outcome.failure_weight()
