"""Repository ports for domain persistence."""

from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from tutoring.domain.entities.catalog import (
    AcademicCatalogSnapshot,
    ExerciseType,
    Subject,
    Topic,
)
from tutoring.domain.entities.session import TutoringSession
from tutoring.domain.entities.student import Student


class StudentRepository(Protocol):
    """Port for Student aggregate persistence."""

    def save(self, student: Student) -> None:
        ...

    def get_by_id(self, student_id: UUID) -> Student | None:
        ...

    def list_all(self) -> Sequence[Student]:
        ...

    def delete(self, student_id: UUID) -> bool:
        ...


class CatalogRepository(Protocol):
    """Port for taxonomic catalog persistence and snapshot resolution."""

    def save_subject(self, subject: Subject) -> None:
        ...

    def save_topic(self, topic: Topic) -> None:
        ...

    def save_exercise_type(self, exercise_type: ExerciseType) -> None:
        ...

    def get_subject(self, subject_id: UUID) -> Subject | None:
        ...

    def get_topic(self, topic_id: UUID) -> Topic | None:
        ...

    def get_exercise_type(self, exercise_type_id: UUID) -> ExerciseType | None:
        ...

    def get_snapshot(self) -> AcademicCatalogSnapshot:
        ...


class SessionRepository(Protocol):
    """Port for TutoringSession aggregate persistence."""

    def save(self, session: TutoringSession) -> None:
        ...

    def get_by_id(self, session_id: UUID) -> TutoringSession | None:
        ...

    def list_by_student(self, student_id: UUID) -> Sequence[TutoringSession]:
        ...
