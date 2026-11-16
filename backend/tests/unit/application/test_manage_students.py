"""Unit tests for T3.3: ManageStudentsUseCase."""

from datetime import date, datetime, timezone
from uuid import uuid4

import pytest

from tutoring.application.dtos import (
    CreateExamGoalDTO,
    CreateStudentDTO,
    RecordExamResultDTO,
)
from tutoring.application.fakes import (
    FakeTrainingTrigger,
    InMemoryCatalogRepository,
    InMemoryStudentRepository,
)
from tutoring.application.use_cases.manage_students import ManageStudentsUseCase
from tutoring.domain.entities.catalog import Subject
from tutoring.domain.exceptions import DuplicateEntityError, EntityNotFoundError, ValidationError


def test_create_student_and_list_and_get_detail() -> None:
    student_repo = InMemoryStudentRepository()
    catalog_repo = InMemoryCatalogRepository()
    use_case = ManageStudentsUseCase(student_repo=student_repo, catalog_repo=catalog_repo)

    created = use_case.create_student(
        CreateStudentDTO(
            full_name="Lucía Morales",
            academic_level="2º Bach",
            pedagogical_notes="Dedicada",
        )
    )

    assert created.full_name == "Lucía Morales"
    assert created.academic_level == "2º Bach"
    assert created.pedagogical_notes == "Dedicada"
    assert created.exam_goals == ()

    students = use_case.list_students()
    assert len(students) == 1
    assert students[0].id == created.id
    assert students[0].full_name == "Lucía Morales"

    detail = use_case.get_student_detail(created.id)
    assert detail.id == created.id
    assert detail.full_name == "Lucía Morales"


def test_add_exam_goal_validates_student_and_subject_existence() -> None:
    student_repo = InMemoryStudentRepository()
    catalog_repo = InMemoryCatalogRepository()
    use_case = ManageStudentsUseCase(student_repo=student_repo, catalog_repo=catalog_repo)

    subject = Subject(id=uuid4(), name="Química")
    catalog_repo.save_subject(subject)

    student = use_case.create_student(
        CreateStudentDTO(full_name="Marcos", academic_level="4º ESO")
    )

    # Missing subject fails
    with pytest.raises(EntityNotFoundError):
        use_case.add_exam_goal(
            student_id=student.id,
            dto=CreateExamGoalDTO(
                subject_id=uuid4(),
                title="Examen",
                exam_date=date(2026, 11, 20),
            ),
            today=date(2026, 11, 16),
        )

    # Missing student fails
    with pytest.raises(EntityNotFoundError):
        use_case.add_exam_goal(
            student_id=uuid4(),
            dto=CreateExamGoalDTO(
                subject_id=subject.id,
                title="Examen",
                exam_date=date(2026, 11, 20),
            ),
            today=date(2026, 11, 16),
        )

    # Valid addition
    goal = use_case.add_exam_goal(
        student_id=student.id,
        dto=CreateExamGoalDTO(
            subject_id=subject.id,
            title="Parcial Termodinámica",
            exam_date=date(2026, 11, 25),
        ),
        today=date(2026, 11, 16),
    )

    assert goal.title == "Parcial Termodinámica"
    detail = use_case.get_student_detail(student.id)
    assert len(detail.exam_goals) == 1
    assert detail.exam_goals[0].id == goal.id


def test_record_exam_result_persists_grade_and_notifies_trigger() -> None:
    student_repo = InMemoryStudentRepository()
    catalog_repo = InMemoryCatalogRepository()
    trigger = FakeTrainingTrigger()
    use_case = ManageStudentsUseCase(
        student_repo=student_repo, catalog_repo=catalog_repo, training_trigger=trigger
    )
    subject = Subject(id=uuid4(), name="Física")
    catalog_repo.save_subject(subject)
    student = use_case.create_student(CreateStudentDTO(full_name="Elena", academic_level="2º Bach"))
    goal = use_case.add_exam_goal(
        student.id,
        CreateExamGoalDTO(subject_id=subject.id, title="Óptica", exam_date=date(2026, 11, 25)),
        today=date(2026, 11, 16),
    )

    updated = use_case.record_exam_result(
        student_id=student.id,
        goal_id=goal.id,
        dto=RecordExamResultDTO(
            score=4.0,
            max_score=10.0,
            recorded_at=datetime(2026, 11, 25, 18, 0, tzinfo=timezone.utc),
            notes="Repasar lentes",
        ),
    )
    assert updated.result is not None
    assert updated.result.score == 4.0
    assert updated.result.is_passing is False
    assert trigger.trigger_count == 1

    with pytest.raises(DuplicateEntityError):
        use_case.record_exam_result(
            student.id,
            goal.id,
            RecordExamResultDTO(score=6.0, recorded_at=datetime(2026, 11, 25, 19, 0, tzinfo=timezone.utc)),
        )
    assert trigger.trigger_count == 1

    # Non-existent student fails
    with pytest.raises(EntityNotFoundError):
        use_case.record_exam_result(
            student_id=uuid4(),
            goal_id=goal.id,
            dto=RecordExamResultDTO(score=7.0, recorded_at=datetime(2026, 11, 25, 19, 0, tzinfo=timezone.utc)),
        )

    # Non-existent goal fails
    with pytest.raises(EntityNotFoundError):
        use_case.record_exam_result(
            student_id=student.id,
            goal_id=uuid4(),
            dto=RecordExamResultDTO(score=7.0, recorded_at=datetime(2026, 11, 25, 19, 0, tzinfo=timezone.utc)),
        )

