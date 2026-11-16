"""Value object representing an upcoming exam or academic goal."""

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from tutoring.domain.exceptions import ValidationError
from tutoring.domain.validation import require_non_empty


@dataclass(frozen=True)
class ExamGoal:
    """Immutable target exam linked to a subject and optional specific topics."""

    id: UUID
    subject_id: UUID
    title: str
    exam_date: date
    topic_ids: tuple[UUID, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "title", require_non_empty(self.title, "title"))
        object.__setattr__(self, "topic_ids", tuple(dict.fromkeys(self.topic_ids)))

    def days_remaining(self, reference_date: date) -> int:
        """Return signed days between reference_date and exam_date."""
        return (self.exam_date - reference_date).days

    def is_upcoming(self, reference_date: date, horizon_days: int = 14) -> bool:
        """Return True if exam occurs within [0, horizon_days] from reference_date."""
        if horizon_days < 0:
            raise ValidationError("horizon_days cannot be negative.")
        remaining = self.days_remaining(reference_date)
        return 0 <= remaining <= horizon_days
