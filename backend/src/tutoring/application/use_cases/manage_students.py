"""Use cases for managing students and their exam goals."""

from datetime import date
from uuid import UUID, uuid4

from tutoring.application.dtos import (
    CreateExamGoalDTO,
    CreateStudentDTO,
    ExamGoalDTO,
    ExamResultDTO,
    RecordExamResultDTO,
    StudentDetailDTO,
    StudentSummaryDTO,
)
from tutoring.domain.entities.student import Student
from tutoring.domain.exceptions import EntityNotFoundError
from tutoring.domain.ports.ml_training import TrainingTriggerPort
from tutoring.domain.ports.repositories import CatalogRepository, StudentRepository
from tutoring.domain.value_objects.exam_goal import ExamGoal, ExamResult


class ManageStudentsUseCase:
    """Orchestrates student registrations, profile queries, and exam goal additions."""

    def __init__(
        self,
        student_repo: StudentRepository,
        catalog_repo: CatalogRepository,
        training_trigger: TrainingTriggerPort | None = None,
    ) -> None:
        self._student_repo = student_repo
        self._catalog_repo = catalog_repo
        self._training_trigger = training_trigger

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
        return self._to_exam_goal_dto(goal)

    def record_exam_result(
        self,
        student_id: UUID,
        goal_id: UUID,
        dto: RecordExamResultDTO,
    ) -> ExamGoalDTO:
        student = self._student_repo.get_by_id(student_id)
        if student is None:
            raise EntityNotFoundError(f"Student '{student_id}' was not found.")

        result = ExamResult(
            score=dto.score,
            recorded_at=dto.recorded_at,
            max_score=dto.max_score,
            notes=dto.notes,
        )
        updated_goal = student.record_exam_result(goal_id=goal_id, result=result)
        self._student_repo.save(student)
        if self._training_trigger is not None:
            self._training_trigger.notify_new_data()
        return self._to_exam_goal_dto(updated_goal)

    @staticmethod
    def _to_exam_goal_dto(goal: ExamGoal) -> ExamGoalDTO:
        result_dto = (
            ExamResultDTO(
                score=goal.result.score,
                max_score=goal.result.max_score,
                normalized_score_10=goal.result.normalized_score_10,
                is_passing=goal.result.is_passing,
                recorded_at=goal.result.recorded_at,
                notes=goal.result.notes,
            )
            if goal.result is not None
            else None
        )
        return ExamGoalDTO(
            id=goal.id,
            subject_id=goal.subject_id,
            title=goal.title,
            exam_date=goal.exam_date,
            topic_ids=goal.topic_ids,
            result=result_dto,
        )

    @classmethod
    def _to_detail_dto(cls, student: Student) -> StudentDetailDTO:
        goal_dtos = tuple(
            cls._to_exam_goal_dto(g)
            for g in student.exam_goals
        )
        return StudentDetailDTO(
            id=student.id,
            full_name=student.full_name,
            academic_level=student.academic_level,
            pedagogical_notes=student.pedagogical_notes,
            exam_goals=goal_dtos,
        )
