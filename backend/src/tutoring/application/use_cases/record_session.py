"""Use case for recording a completed tutoring session and its exercise attempts."""

from uuid import UUID, uuid4

from tutoring.application.dtos import ExerciseAttemptDTO, RecordSessionDTO, SessionDTO
from tutoring.domain.entities.session import TutoringSession
from tutoring.domain.exceptions import EntityNotFoundError
from tutoring.domain.ports.repositories import (
    CatalogRepository,
    SessionRepository,
    StudentRepository,
)
from tutoring.domain.value_objects.attempt import ExerciseAttempt


class RecordSessionUseCase:
    """Validates existence of student and exercise types before saving a tutoring session."""

    def __init__(
        self,
        student_repo: StudentRepository,
        catalog_repo: CatalogRepository,
        session_repo: SessionRepository,
    ) -> None:
        self._student_repo = student_repo
        self._catalog_repo = catalog_repo
        self._session_repo = session_repo

    def execute(self, student_id: UUID, dto: RecordSessionDTO) -> SessionDTO:
        student = self._student_repo.get_by_id(student_id)
        if student is None:
            raise EntityNotFoundError(f"Student '{student_id}' was not found.")

        snapshot = self._catalog_repo.get_snapshot()
        attempts: list[ExerciseAttempt] = []
        for attempt_input in dto.attempts:
            # Validates existence of exercise_type_id in catalog
            snapshot.get_exercise_type(attempt_input.exercise_type_id)
            attempts.append(
                ExerciseAttempt(
                    exercise_type_id=attempt_input.exercise_type_id,
                    outcome=attempt_input.outcome,
                    error_cause=attempt_input.error_cause,
                    notes=attempt_input.notes,
                )
            )

        session = TutoringSession(
            id=uuid4(),
            student_id=student_id,
            occurred_at=dto.occurred_at,
            duration_minutes=dto.duration_minutes,
            session_notes=dto.session_notes,
            attempts=attempts,
        )
        self._session_repo.save(session)
        return self._to_dto(session)

    def list_student_sessions(self, student_id: UUID) -> tuple[SessionDTO, ...]:
        student = self._student_repo.get_by_id(student_id)
        if student is None:
            raise EntityNotFoundError(f"Student '{student_id}' was not found.")
        sessions = self._session_repo.list_by_student(student_id)
        return tuple(
            self._to_dto(s)
            for s in sorted(sessions, key=lambda s: s.occurred_at, reverse=True)
        )

    @staticmethod
    def _to_dto(session: TutoringSession) -> SessionDTO:
        attempt_dtos = tuple(
            ExerciseAttemptDTO(
                exercise_type_id=a.exercise_type_id,
                outcome=a.outcome,
                error_cause=a.error_cause,
                notes=a.notes,
                severity_weight=a.severity_weight(),
            )
            for a in session.attempts
        )
        return SessionDTO(
            id=session.id,
            student_id=session.student_id,
            occurred_at=session.occurred_at,
            duration_minutes=session.duration_minutes,
            session_notes=session.session_notes,
            failure_rate=session.failure_rate(),
            attempts=attempt_dtos,
        )
