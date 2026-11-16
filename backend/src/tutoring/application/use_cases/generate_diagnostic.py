"""Use case for generating personalized diagnostic insights for a student."""

from datetime import date
from uuid import UUID

from tutoring.application.dtos import StudentDiagnosticDTO
from tutoring.domain.exceptions import EntityNotFoundError
from tutoring.domain.ports.analyzer import PedagogicalAnalyzerPort
from tutoring.domain.ports.repositories import (
    CatalogRepository,
    SessionRepository,
    StudentRepository,
)


class GenerateStudentDiagnosticUseCase:
    """Loads student memory and delegates diagnostic analysis to PedagogicalAnalyzerPort."""

    def __init__(
        self,
        student_repo: StudentRepository,
        catalog_repo: CatalogRepository,
        session_repo: SessionRepository,
        analyzer: PedagogicalAnalyzerPort,
    ) -> None:
        self._student_repo = student_repo
        self._catalog_repo = catalog_repo
        self._session_repo = session_repo
        self._analyzer = analyzer

    def execute(self, student_id: UUID, reference_date: date) -> StudentDiagnosticDTO:
        student = self._student_repo.get_by_id(student_id)
        if student is None:
            raise EntityNotFoundError(f"Student '{student_id}' was not found.")

        sessions = self._session_repo.list_by_student(student_id)
        catalog_snapshot = self._catalog_repo.get_snapshot()

        diagnostic = self._analyzer.analyze(
            student=student,
            sessions=sessions,
            catalog=catalog_snapshot,
            reference_date=reference_date,
        )

        return StudentDiagnosticDTO(
            student_id=diagnostic.student_id,
            generated_at=diagnostic.generated_at,
            analyzer_name=diagnostic.analyzer_name,
            subject_priorities=diagnostic.subject_priorities,
            weak_exercise_types=diagnostic.weak_exercise_types,
            exam_alerts=diagnostic.exam_alerts,
            overall_trend=diagnostic.overall_trend,
        )
