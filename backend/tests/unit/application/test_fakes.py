"""Unit tests for T3.1: In-memory repositories."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from tutoring.application.fakes import (
    InMemoryCatalogRepository,
    InMemorySessionRepository,
    InMemoryStudentRepository,
)
from tutoring.domain.entities.catalog import ExerciseType, Subject, Topic
from tutoring.domain.entities.session import TutoringSession
from tutoring.domain.entities.student import Student
from tutoring.domain.enums import AttemptOutcome
from tutoring.domain.value_objects.attempt import ExerciseAttempt


def test_in_memory_student_repository() -> None:
    repo = InMemoryStudentRepository()
    student = Student(id=uuid4(), full_name="Pedro", academic_level="ESO")

    assert repo.list_all() == ()
    assert repo.get_by_id(student.id) is None
    assert repo.delete(student.id) is False

    repo.save(student)
    assert repo.get_by_id(student.id) == student
    assert repo.list_all() == (student,)

    student.rename("Pedro García")
    repo.save(student)
    assert repo.get_by_id(student.id) is not None
    assert repo.get_by_id(student.id).full_name == "Pedro García"  # type: ignore[union-attr]

    assert repo.delete(student.id) is True
    assert repo.get_by_id(student.id) is None
    assert repo.list_all() == ()


def test_in_memory_catalog_repository() -> None:
    repo = InMemoryCatalogRepository()
    subject = Subject(id=uuid4(), name="Matemáticas")
    topic = Topic(id=uuid4(), subject_id=subject.id, name="Álgebra")
    ex_type = ExerciseType(id=uuid4(), topic_id=topic.id, name="Ecuaciones")

    assert repo.get_subject(subject.id) is None
    assert repo.get_topic(topic.id) is None
    assert repo.get_exercise_type(ex_type.id) is None

    repo.save_subject(subject)
    repo.save_topic(topic)
    repo.save_exercise_type(ex_type)

    assert repo.get_subject(subject.id) == subject
    assert repo.get_topic(topic.id) == topic
    assert repo.get_exercise_type(ex_type.id) == ex_type

    snapshot = repo.get_snapshot()
    assert snapshot.get_subject(subject.id) == subject
    assert snapshot.resolve_exercise_path(ex_type.id) == (subject, topic, ex_type)


def test_in_memory_session_repository() -> None:
    repo = InMemorySessionRepository()
    student_id = uuid4()
    session = TutoringSession(
        id=uuid4(),
        student_id=student_id,
        occurred_at=datetime(2026, 11, 16, 10, 0, tzinfo=timezone.utc),
        duration_minutes=60,
        attempts=[ExerciseAttempt(uuid4(), AttemptOutcome.SUCCESS)],
    )

    assert repo.get_by_id(session.id) is None
    assert repo.list_by_student(student_id) == ()

    repo.save(session)
    assert repo.get_by_id(session.id) == session
    assert repo.list_by_student(student_id) == (session,)
    assert repo.list_by_student(uuid4()) == ()
