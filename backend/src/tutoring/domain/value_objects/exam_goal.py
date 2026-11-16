"""Value objects representing upcoming exams and evaluation results."""

from dataclasses import dataclass, replace
from datetime import date, datetime
import math
from uuid import UUID

from tutoring.domain.exceptions import DuplicateEntityError, ValidationError
from tutoring.domain.validation import require_non_empty


@dataclass(frozen=True)
class ExamResult:
    """Immutable evaluation result of an exam goal."""

    score: float
    recorded_at: datetime
    max_score: float = 10.0
    notes: str = ""

    def __post_init__(self) -> None:
        if not math.isfinite(self.score):
            raise ValidationError("ExamResult score must be a finite number.")
        if not math.isfinite(self.max_score):
            raise ValidationError("ExamResult max_score must be a finite number.")
        if self.max_score <= 0.0:
            raise ValidationError("ExamResult max_score must be strictly positive.")
        if not (0.0 <= self.score <= self.max_score):
            raise ValidationError(
                f"ExamResult score {self.score} must be between 0.0 and max_score {self.max_score}."
            )
        object.__setattr__(self, "notes", self.notes.strip())

    @property
    def normalized_score_10(self) -> float:
        """Return score scaled to a 0.0 - 10.0 standard range, rounded to 4 decimals."""
        return round((self.score / self.max_score) * 10.0, 4)

    @property
    def is_passing(self) -> bool:
        """Return True if normalized score is at or above standard passing grade (5.0)."""
        return self.normalized_score_10 >= 5.0


@dataclass(frozen=True)
class ExamGoal:
    """Immutable target exam linked to a subject and optional specific topics."""

    id: UUID
    subject_id: UUID
    title: str
    exam_date: date
    topic_ids: tuple[UUID, ...] = ()
    result: ExamResult | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "title", require_non_empty(self.title, "title"))
        object.__setattr__(self, "topic_ids", tuple(dict.fromkeys(self.topic_ids)))

    def days_remaining(self, reference_date: date) -> int:
        """Return signed days between reference_date and exam_date."""
        return (self.exam_date - reference_date).days

    def is_upcoming(self, reference_date: date, horizon_days: int = 14) -> bool:
        """Return True if exam occurs within [0, horizon_days] from reference_date and has no result."""
        if horizon_days < 0:
            raise ValidationError("horizon_days cannot be negative.")
        if self.result is not None:
            return False
        remaining = self.days_remaining(reference_date)
        return 0 <= remaining <= horizon_days

    def with_result(self, result: ExamResult) -> "ExamGoal":
        """Return a copy of this goal with an evaluated result attached."""
        if self.result is not None:
            raise DuplicateEntityError(
                f"Exam goal '{self.id}' already has an evaluation result recorded."
            )
        return replace(self, result=result)
