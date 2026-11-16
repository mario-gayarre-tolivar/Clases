"""Application Data Transfer Objects."""

from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

from tutoring.domain.enums import AttemptOutcome, ErrorCause, LearningTrend
from tutoring.domain.value_objects.diagnostic import (
    ExamAlert,
    SubjectPriority,
    WeakExerciseType,
)


@dataclass(frozen=True)
class CreateSubjectDTO:
    name: str
    description: str = ""


@dataclass(frozen=True)
class SubjectDTO:
    id: UUID
    name: str
    description: str


@dataclass(frozen=True)
class CreateTopicDTO:
    subject_id: UUID
    name: str


@dataclass(frozen=True)
class TopicDTO:
    id: UUID
    subject_id: UUID
    name: str


@dataclass(frozen=True)
class CreateExerciseTypeDTO:
    topic_id: UUID
    name: str
    description: str = ""


@dataclass(frozen=True)
class ExerciseTypeDTO:
    id: UUID
    topic_id: UUID
    name: str
    description: str


@dataclass(frozen=True)
class CatalogTreeTopicDTO:
    id: UUID
    name: str
    exercise_types: tuple[ExerciseTypeDTO, ...]


@dataclass(frozen=True)
class CatalogTreeSubjectDTO:
    id: UUID
    name: str
    description: str
    topics: tuple[CatalogTreeTopicDTO, ...]


@dataclass(frozen=True)
class CatalogTreeDTO:
    subjects: tuple[CatalogTreeSubjectDTO, ...]


@dataclass(frozen=True)
class CreateStudentDTO:
    full_name: str
    academic_level: str
    pedagogical_notes: str = ""


@dataclass(frozen=True)
class ExamGoalDTO:
    id: UUID
    subject_id: UUID
    title: str
    exam_date: date
    topic_ids: tuple[UUID, ...]


@dataclass(frozen=True)
class StudentSummaryDTO:
    id: UUID
    full_name: str
    academic_level: str


@dataclass(frozen=True)
class StudentDetailDTO:
    id: UUID
    full_name: str
    academic_level: str
    pedagogical_notes: str
    exam_goals: tuple[ExamGoalDTO, ...]


@dataclass(frozen=True)
class CreateExamGoalDTO:
    subject_id: UUID
    title: str
    exam_date: date
    topic_ids: tuple[UUID, ...] = ()


@dataclass(frozen=True)
class ExerciseAttemptInputDTO:
    exercise_type_id: UUID
    outcome: AttemptOutcome
    error_cause: ErrorCause | None = None
    notes: str = ""


@dataclass(frozen=True)
class ExerciseAttemptDTO:
    exercise_type_id: UUID
    outcome: AttemptOutcome
    error_cause: ErrorCause | None
    notes: str
    severity_weight: float


@dataclass(frozen=True)
class RecordSessionDTO:
    occurred_at: datetime
    duration_minutes: int
    session_notes: str = ""
    attempts: tuple[ExerciseAttemptInputDTO, ...] = ()


@dataclass(frozen=True)
class SessionDTO:
    id: UUID
    student_id: UUID
    occurred_at: datetime
    duration_minutes: int
    session_notes: str
    failure_rate: float
    attempts: tuple[ExerciseAttemptDTO, ...]


@dataclass(frozen=True)
class StudentDiagnosticDTO:
    student_id: UUID
    generated_at: datetime
    analyzer_name: str
    subject_priorities: tuple[SubjectPriority, ...]
    weak_exercise_types: tuple[WeakExerciseType, ...]
    exam_alerts: tuple[ExamAlert, ...]
    overall_trend: LearningTrend
