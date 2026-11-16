"""Integration tests for T4.2: SQLite student repository."""

from datetime import date
from uuid import uuid4

import pytest

from tutoring.domain.entities.catalog import Subject
from tutoring.domain.entities.student import Student
from tutoring.domain.value_objects.exam_goal import ExamGoal
from tutoring.infrastructure.persistence.sqlite_catalog_repo import (
    SqliteCatalogRepository,
)
from tutoring.infrastructure.persistence.sqlite_db import init_sqlite_db
from tutoring.infrastructure.persistence.sqlite_student_repo import (
    SqliteStudentRepository,
)


def test_sqlite_student_persistence_lifecycle() -> None:
    conn = init_sqlite_db(":memory:")
    catalog_repo = SqliteCatalogRepository(conn)
    student_repo = SqliteStudentRepository(conn)

    subject = Subject(id=uuid4(), name="Historia")
    catalog_repo.save_subject(subject)

    student = Student(
        id=uuid4(),
        full_name="Guillermo",
        academic_level="1º Bach",
        pedagogical_notes="Atento",
    )
    goal = ExamGoal(
        id=uuid4(),
        subject_id=subject.id,
        title="Revolución Francesa",
        exam_date=date(2026, 11, 28),
        topic_ids=(uuid4(),),
    )
    student.add_exam_goal(goal, today=date(2026, 11, 16))

    assert student_repo.get_by_id(student.id) is None
    assert student_repo.list_all() == ()

    student_repo.save(student)

    loaded = student_repo.get_by_id(student.id)
    assert loaded is not None
    assert loaded.id == student.id
    assert loaded.full_name == "Guillermo"
    assert loaded.academic_level == "1º Bach"
    assert loaded.pedagogical_notes == "Atento"
    assert len(loaded.exam_goals) == 1
    assert loaded.exam_goals[0] == goal

    all_students = student_repo.list_all()
    assert len(all_students) == 1
    assert all_students[0].id == student.id

    assert student_repo.delete(student.id) is True
    assert student_repo.get_by_id(student.id) is None
    assert student_repo.delete(student.id) is False
