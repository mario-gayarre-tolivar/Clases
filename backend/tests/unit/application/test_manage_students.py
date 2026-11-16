"""Unit tests for T3.3: ManageStudentsUseCase."""

from datetime import date
from uuid import uuid4

import pytest

from tutoring.application.dtos import (
    CreateExamGoalDTO,
    CreateStudentDTO,
)
from tutoring.application.fakes import InMemoryCatalogRepository, InMemoryStudentRepository
from tutoring.application.use_cases.manage_students import ManageStudentsUseCase
from tutoring.domain.entities.catalog import Subject
from tutoring.domain.exceptions import EntityNotFoundError, ValidationError


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
