"""Use cases for managing students and their exam goals."""

from datetime import date
from uuid import UUID, uuid4

from tutoring.application.dtos import (
    CreateExamGoalDTO,
    CreateStudentDTO,
    ExamGoalDTO,
    StudentDetailDTO,
    StudentSummaryDTO,
)
from tutoring.domain.entities.student import Student
from tutoring.domain.exceptions import EntityNotFoundError
from tutoring.domain.ports.repositories import CatalogRepository, StudentRepository
from tutoring.domain.value_objects.exam_goal import ExamGoal


class ManageStudentsUseCase:
    """Orchestrates student registrations, profile queries, and exam goal additions."""

    def __init__(
        self,
        student_repo: StudentRepository,
        catalog_repo: CatalogRepository,
    ) -> None:
        self._student_repo = student_repo
        self._catalog_repo = catalog_repo

    def create_student(self, dto: CreateStudentDTO) -> StudentDetailDTO:
        student = Student(
            id=uuid4(),
            full_name=dto.full_name,
            academic_level=dto.academic_level,
            pedagogical_notes=dto.pedagogical_notes,
        )
        self._student_repo.save(student)
        return self._to_detail_dto(student)

    def list_students(self) -> tuple[StudentSummaryDTO, ...]:
        students = self._student_repo.list_all()
        return tuple(
            StudentSummaryDTO(
                id=s.id,
                full_name=s.full_name,
                academic_level=s.academic_level,
            )
            for s in sorted(students, key=lambda s: s.full_name)
        )

    def get_student_detail(self, student_id: UUID) -> StudentDetailDTO:
        student = self._student_repo.get_by_id(student_id)
        if student is None:
            raise EntityNotFoundError(f"Student '{student_id}' was not found.")
        return self._to_detail_dto(student)

    def add_exam_goal(
        self,
        student_id: UUID,
        dto: CreateExamGoalDTO,
        today: date,
    ) -> ExamGoalDTO:
        student = self._student_repo.get_by_id(student_id)
        if student is None:
            raise EntityNotFoundError(f"Student '{student_id}' was not found.")

        # Ensure subject exists
        subject = self._catalog_repo.get_subject(dto.subject_id)
        if subject is None:
            raise EntityNotFoundError(f"Subject '{dto.subject_id}' was not found.")

        goal = ExamGoal(
            id=uuid4(),
            subject_id=dto.subject_id,
            title=dto.title,
            exam_date=dto.exam_date,
            topic_ids=dto.topic_ids,
        )
        student.add_exam_goal(goal, today=today)
        self._student_repo.save(student)
        return ExamGoalDTO(
            id=goal.id,
            subject_id=goal.subject_id,
            title=goal.title,
            exam_date=goal.exam_date,
            topic_ids=goal.topic_ids,
        )

    @staticmethod
    def _to_detail_dto(student: Student) -> StudentDetailDTO:
        goal_dtos = tuple(
            ExamGoalDTO(
                id=g.id,
                subject_id=g.subject_id,
                title=g.title,
                exam_date=g.exam_date,
                topic_ids=g.topic_ids,
            )
            for g in student.exam_goals
        )
        return StudentDetailDTO(
            id=student.id,
            full_name=student.full_name,
            academic_level=student.academic_level,
            pedagogical_notes=student.pedagogical_notes,
            exam_goals=goal_dtos,
        )
