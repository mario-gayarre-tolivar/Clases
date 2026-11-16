"""Unit tests for T1.3: Student entity and ExamGoal value object."""

from datetime import date, datetime, timezone
from uuid import uuid4

import pytest

from tutoring.domain.entities.student import Student
from tutoring.domain.exceptions import (
    DuplicateEntityError,
    EntityNotFoundError,
    ValidationError,
)
from tutoring.domain.value_objects.exam_goal import ExamGoal, ExamResult


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


def test_exam_result_validates_bounds_and_normalizes_score() -> None:
    ts = datetime(2026, 11, 16, 18, 0, tzinfo=timezone.utc)
    passing = ExamResult(score=5.0, max_score=10.0, recorded_at=ts, notes="  Justo  ")
    assert passing.normalized_score_10 == 5.0
    assert passing.is_passing is True
    assert passing.notes == "Justo"

    scaled_fail = ExamResult(score=49.0, max_score=100.0, recorded_at=ts)
    assert scaled_fail.normalized_score_10 == 4.9
    assert scaled_fail.is_passing is False

    for bad_score, bad_max in [(-0.1, 10.0), (10.5, 10.0), (5.0, 0.0), (float("nan"), 10.0)]:
        with pytest.raises(ValidationError):
            ExamResult(score=bad_score, max_score=bad_max, recorded_at=ts)


def test_exam_goal_with_result_is_no_longer_upcoming() -> None:
    today = date(2026, 11, 16)
    goal = ExamGoal(id=uuid4(), subject_id=uuid4(), title="Parcial", exam_date=today)
    assert goal.is_upcoming(today, horizon_days=14) is True

    result = ExamResult(score=7.5, recorded_at=datetime(2026, 11, 16, 18, 0, tzinfo=timezone.utc))
    evaluated = goal.with_result(result)
    assert evaluated.result == result
    assert evaluated.is_upcoming(today, horizon_days=14) is False

    with pytest.raises(DuplicateEntityError):
        evaluated.with_result(result)


def test_student_record_exam_result_lifecycle() -> None:
    today = date(2026, 11, 16)
    student = Student(id=uuid4(), full_name="Sofía", academic_level="2º ESO")
    goal = ExamGoal(id=uuid4(), subject_id=uuid4(), title="Álgebra", exam_date=date(2026, 11, 20))
    student.add_exam_goal(goal, today=today)

    result = ExamResult(score=4.2, recorded_at=datetime(2026, 11, 20, 17, 0, tzinfo=timezone.utc))
    with pytest.raises(EntityNotFoundError):
        student.record_exam_result(uuid4(), result)

    updated = student.record_exam_result(goal.id, result)
    assert updated.result == result
    assert student.exam_goals[0].result == result

    with pytest.raises(DuplicateEntityError):
        student.record_exam_result(goal.id, result)

