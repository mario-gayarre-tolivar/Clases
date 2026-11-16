"""Diagnostic output value objects produced by pedagogical analyzers."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from tutoring.domain.enums import ErrorCause, LearningTrend


@dataclass(frozen=True)
class SubjectPriority:
    """Ranked focus recommendation for a single academic subject."""

    subject_id: UUID
    subject_name: str
    priority_score: float
    weighted_failure_rate: float
    upcoming_exam_days: int | None
    trend: LearningTrend
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class WeakExerciseType:
    """Exercise category exhibiting notable failure rate and dominant error cause."""

    exercise_type_id: UUID
    exercise_type_name: str
    topic_name: str
    subject_name: str
    attempts_count: int
    weighted_failure_rate: float
    dominant_error_cause: ErrorCause | None


@dataclass(frozen=True)
class ExamAlert:
    """Readiness alert for an upcoming exam goal."""

    exam_goal_id: UUID
    subject_name: str
    title: str
    days_remaining: int
    readiness_risk: str


@dataclass(frozen=True)
class StudentDiagnostic:
    """Complete deterministic or ML-backed diagnostic for a student."""

    student_id: UUID
    generated_at: datetime
    analyzer_name: str
    subject_priorities: tuple[SubjectPriority, ...]
    weak_exercise_types: tuple[WeakExerciseType, ...]
    exam_alerts: tuple[ExamAlert, ...]
    overall_trend: LearningTrend
