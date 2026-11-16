"""Domain value objects."""

from tutoring.domain.value_objects.attempt import ExerciseAttempt
from tutoring.domain.value_objects.diagnostic import (
    ExamAlert,
    StudentDiagnostic,
    SubjectPriority,
    WeakExerciseType,
)
from tutoring.domain.value_objects.exam_goal import ExamGoal, ExamResult

__all__ = [
    "ExamAlert",
    "ExamGoal",
    "ExamResult",
    "ExerciseAttempt",
    "StudentDiagnostic",
    "SubjectPriority",
    "WeakExerciseType",
]
