"""Domain value objects."""

from tutoring.domain.value_objects.attempt import ExerciseAttempt
from tutoring.domain.value_objects.diagnostic import (
    ExamAlert,
    StudentDiagnostic,
    SubjectPriority,
    WeakExerciseType,
)
from tutoring.domain.value_objects.exam_goal import ExamGoal

__all__ = [
    "ExamAlert",
    "ExamGoal",
    "ExerciseAttempt",
    "StudentDiagnostic",
    "SubjectPriority",
    "WeakExerciseType",
]
