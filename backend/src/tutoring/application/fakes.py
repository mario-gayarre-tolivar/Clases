"""In-memory test doubles implementing domain repository ports."""

from collections.abc import Sequence
from uuid import UUID

from tutoring.domain.entities.catalog import (
    AcademicCatalogSnapshot,
    ExerciseType,
    Subject,
    Topic,
)
from tutoring.domain.entities.session import TutoringSession
from tutoring.domain.entities.student import Student
from tutoring.domain.ports.repositories import (
    CatalogRepository,
    SessionRepository,
    StudentRepository,
)


class InMemoryStudentRepository(StudentRepository):
    """Fake repository storing students in memory."""

    def __init__(self) -> None:
        self._students: dict[UUID, Student] = {}

    def save(self, student: Student) -> None:
        self._students[student.id] = student

    def get_by_id(self, student_id: UUID) -> Student | None:
        return self._students.get(student_id)

    def list_all(self) -> Sequence[Student]:
        return tuple(self._students.values())

    def delete(self, student_id: UUID) -> bool:
        if student_id in self._students:
            del self._students[student_id]
            return True
        return False


class InMemoryCatalogRepository(CatalogRepository):
    """Fake repository storing catalog items in memory."""

    def __init__(self) -> None:
        self._subjects: dict[UUID, Subject] = {}
        self._topics: dict[UUID, Topic] = {}
        self._exercise_types: dict[UUID, ExerciseType] = {}

    def save_subject(self, subject: Subject) -> None:
        self._subjects[subject.id] = subject

    def save_topic(self, topic: Topic) -> None:
        self._topics[topic.id] = topic

    def save_exercise_type(self, exercise_type: ExerciseType) -> None:
        self._exercise_types[exercise_type.id] = exercise_type

    def get_subject(self, subject_id: UUID) -> Subject | None:
        return self._subjects.get(subject_id)

    def get_topic(self, topic_id: UUID) -> Topic | None:
        return self._topics.get(topic_id)

    def get_exercise_type(self, exercise_type_id: UUID) -> ExerciseType | None:
        return self._exercise_types.get(exercise_type_id)

    def get_snapshot(self) -> AcademicCatalogSnapshot:
        return AcademicCatalogSnapshot(
            subjects=list(self._subjects.values()),
            topics=list(self._topics.values()),
            exercise_types=list(self._exercise_types.values()),
        )


class InMemorySessionRepository(SessionRepository):
    """Fake repository storing tutoring sessions in memory."""

    def __init__(self) -> None:
        self._sessions: dict[UUID, TutoringSession] = {}

    def save(self, session: TutoringSession) -> None:
        self._sessions[session.id] = session

    def get_by_id(self, session_id: UUID) -> TutoringSession | None:
        return self._sessions.get(session_id)

    def list_by_student(self, student_id: UUID) -> Sequence[TutoringSession]:
        return tuple(
            session
            for session in self._sessions.values()
            if session.student_id == student_id
        )
