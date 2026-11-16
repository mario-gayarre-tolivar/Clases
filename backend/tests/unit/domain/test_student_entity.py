"""Unit tests for T1.3: Student entity and ExamGoal value object."""

from datetime import date
from uuid import uuid4

import pytest

from tutoring.domain.entities.student import Student
from tutoring.domain.exceptions import DuplicateEntityError, ValidationError
from tutoring.domain.value_objects.exam_goal import ExamGoal


def test_exam_goal_validates_title_and_computes_days_remaining() -> None:
    topic_a = uuid4()
    goal = ExamGoal(
        id=uuid4(),
        subject_id=uuid4(),
        title="  Parcial Derivadas  ",
        exam_date=date(2026, 11, 26),
        topic_ids=(topic_a, topic_a),
    )

    assert goal.title == "Parcial Derivadas"
    assert goal.topic_ids == (topic_a,)
    assert goal.days_remaining(date(2026, 11, 16)) == 10
    assert goal.days_remaining(date(2026, 11, 26)) == 0
    assert goal.days_remaining(date(2026, 11, 28)) == -2

    assert goal.is_upcoming(date(2026, 11, 16), horizon_days=14) is True
    assert goal.is_upcoming(date(2026, 11, 16), horizon_days=10) is True
    assert goal.is_upcoming(date(2026, 11, 16), horizon_days=9) is False
    assert goal.is_upcoming(date(2026, 11, 27), horizon_days=14) is False


def test_exam_goal_rejects_blank_title_and_negative_horizon() -> None:
    with pytest.raises(ValidationError):
        ExamGoal(
            id=uuid4(),
            subject_id=uuid4(),
            title="   ",
            exam_date=date(2026, 12, 1),
        )

    goal = ExamGoal(
        id=uuid4(),
        subject_id=uuid4(),
        title="Global",
        exam_date=date(2026, 12, 1),
    )
    with pytest.raises(ValidationError):
        goal.is_upcoming(date(2026, 11, 16), horizon_days=-1)


def test_student_validates_profile_fields_and_updates() -> None:
    student = Student(
        id=uuid4(),
        full_name="  Lucía Pérez  ",
        academic_level="  2º Bachillerato  ",
        pedagogical_notes="  Visual learner  ",
    )

    assert student.full_name == "Lucía Pérez"
    assert student.academic_level == "2º Bachillerato"
    assert student.pedagogical_notes == "Visual learner"
    assert student.exam_goals == ()

    student.rename("  Lucía P. Gómez  ")
    student.update_academic_level("  1º Universidad  ")
    student.update_pedagogical_notes("  Prefiere ejemplos prácticos  ")

    assert student.full_name == "Lucía P. Gómez"
    assert student.academic_level == "1º Universidad"
    assert student.pedagogical_notes == "Prefiere ejemplos prácticos"


def test_student_rejects_blank_required_fields() -> None:
    with pytest.raises(ValidationError):
        Student(id=uuid4(), full_name="", academic_level="4º ESO")
    with pytest.raises(ValidationError):
        Student(id=uuid4(), full_name="Carlos", academic_level="   ")

    student = Student(id=uuid4(), full_name="Carlos", academic_level="4º ESO")
    with pytest.raises(ValidationError):
        student.rename(" ")
    with pytest.raises(ValidationError):
        student.update_academic_level("")
    with pytest.raises(ValidationError):
        student.upcoming_exams(date(2026, 11, 16), horizon_days=-1)


def test_student_add_exam_goal_validates_past_date_and_duplicates() -> None:
    today = date(2026, 11, 16)
    subject_id = uuid4()
    student = Student(id=uuid4(), full_name="Ana", academic_level="1º Bach")

    past_goal = ExamGoal(
        id=uuid4(),
        subject_id=subject_id,
        title="Examen pasado",
        exam_date=date(2026, 11, 15),
    )
    with pytest.raises(ValidationError):
        student.add_exam_goal(past_goal, today=today)

    goal1 = ExamGoal(
        id=uuid4(),
        subject_id=subject_id,
        title="Evaluación 1",
        exam_date=date(2026, 11, 20),
    )
    student.add_exam_goal(goal1, today=today)
    assert student.exam_goals == (goal1,)

    # Same ID rejected
    with pytest.raises(DuplicateEntityError):
        student.add_exam_goal(
            ExamGoal(
                id=goal1.id,
                subject_id=subject_id,
                title="Otro nombre",
                exam_date=date(2026, 11, 25),
            ),
            today=today,
        )

    # Logical duplicate (same subject, normalized title, and date) rejected
    with pytest.raises(DuplicateEntityError):
        student.add_exam_goal(
            ExamGoal(
                id=uuid4(),
                subject_id=subject_id,
                title="  evaluación 1 ",
                exam_date=date(2026, 11, 20),
            ),
            today=today,
        )


def test_student_upcoming_exams_filters_and_sorts_chronologically() -> None:
    today = date(2026, 11, 16)
    subject_id = uuid4()
    past = ExamGoal(uuid4(), subject_id, "Pasado", date(2026, 11, 10))
    in_12_days = ExamGoal(uuid4(), subject_id, "En 12 días", date(2026, 11, 28))
    in_3_days = ExamGoal(uuid4(), subject_id, "En 3 días", date(2026, 11, 19))
    in_30_days = ExamGoal(uuid4(), subject_id, "Lejano", date(2026, 12, 16))

    student = Student(
        id=uuid4(),
        full_name="Mario",
        academic_level="3º ESO",
        exam_goals=[past, in_12_days, in_3_days, in_30_days],
    )

    upcoming = student.upcoming_exams(reference_date=today, horizon_days=14)
    assert upcoming == [in_3_days, in_12_days]
