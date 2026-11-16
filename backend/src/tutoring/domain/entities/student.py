"""Student aggregate root entity."""

from collections.abc import Sequence
from datetime import date
from uuid import UUID

from tutoring.domain.exceptions import DuplicateEntityError, ValidationError
from tutoring.domain.validation import require_non_empty
from tutoring.domain.value_objects.exam_goal import ExamGoal


class Student:
    """Aggregate root holding a student's profile, pedagogical notes, and exam goals."""

    def __init__(
        self,
        id: UUID,
        full_name: str,
        academic_level: str,
        pedagogical_notes: str = "",
        exam_goals: Sequence[ExamGoal] = (),
    ) -> None:
        self._id = id
        self._full_name = require_non_empty(full_name, "full_name")
        self._academic_level = require_non_empty(academic_level, "academic_level")
        self._pedagogical_notes = pedagogical_notes.strip()
        self._exam_goals: list[ExamGoal] = []
        for goal in exam_goals:
            self._append_unique_exam_goal(goal)

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def full_name(self) -> str:
        return self._full_name

    @property
    def academic_level(self) -> str:
        return self._academic_level

    @property
    def pedagogical_notes(self) -> str:
        return self._pedagogical_notes

    @property
    def exam_goals(self) -> tuple[ExamGoal, ...]:
        return tuple(self._exam_goals)

    def add_exam_goal(self, goal: ExamGoal, today: date) -> None:
        """Register a new non-past, non-duplicate exam goal for this student."""
        if goal.exam_date < today:
            raise ValidationError("Exam goal date cannot be in the past.")
        self._append_unique_exam_goal(goal)

    def upcoming_exams(
        self, reference_date: date, horizon_days: int = 14
    ) -> list[ExamGoal]:
        """Return exam goals falling within [0, horizon_days], sorted chronologically."""
        if horizon_days < 0:
            raise ValidationError("horizon_days cannot be negative.")
        upcoming = [
            goal
            for goal in self._exam_goals
            if goal.is_upcoming(reference_date, horizon_days=horizon_days)
        ]
        return sorted(upcoming, key=lambda goal: goal.exam_date)

    def update_pedagogical_notes(self, notes: str) -> None:
        """Update normalized qualitative pedagogical notes."""
        self._pedagogical_notes = notes.strip()

    def update_academic_level(self, academic_level: str) -> None:
        """Validate and update the student's academic level."""
        self._academic_level = require_non_empty(academic_level, "academic_level")

    def rename(self, full_name: str) -> None:
        """Validate and update the student's full name."""
        self._full_name = require_non_empty(full_name, "full_name")

    def _append_unique_exam_goal(self, goal: ExamGoal) -> None:
        for existing in self._exam_goals:
            if existing.id == goal.id:
                raise DuplicateEntityError(f"Duplicate exam goal id '{goal.id}'.")
            if (
                existing.subject_id == goal.subject_id
                and existing.exam_date == goal.exam_date
                and existing.title.casefold() == goal.title.casefold()
            ):
                raise DuplicateEntityError(
                    f"Duplicate exam goal '{goal.title}' on {goal.exam_date}."
                )
        self._exam_goals.append(goal)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Student):
            return NotImplemented
        return (
            self._id == other._id
            and self._full_name == other._full_name
            and self._academic_level == other._academic_level
            and self._pedagogical_notes == other._pedagogical_notes
            and self._exam_goals == other._exam_goals
        )

    def __repr__(self) -> str:
        return (
            f"Student(id={self._id!r}, full_name={self._full_name!r}, "
            f"academic_level={self._academic_level!r})"
        )
