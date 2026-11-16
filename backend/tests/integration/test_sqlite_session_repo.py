"""Integration tests for T4.3: SQLite session repository."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest

from tutoring.domain.entities.catalog import ExerciseType, Subject, Topic
from tutoring.domain.entities.session import TutoringSession
from tutoring.domain.entities.student import Student
from tutoring.domain.enums import AttemptOutcome, ErrorCause
from tutoring.domain.value_objects.attempt import ExerciseAttempt
from tutoring.infrastructure.persistence.sqlite_catalog_repo import (
    SqliteCatalogRepository,
)
from tutoring.infrastructure.persistence.sqlite_db import init_sqlite_db
from tutoring.infrastructure.persistence.sqlite_session_repo import (
    SqliteSessionRepository,
)
from tutoring.infrastructure.persistence.sqlite_student_repo import (
    SqliteStudentRepository,
)


def test_sqlite_session_persistence_lifecycle() -> None:
    conn = init_sqlite_db(":memory:")
    catalog_repo = SqliteCatalogRepository(conn)
    student_repo = SqliteStudentRepository(conn)
    session_repo = SqliteSessionRepository(conn)

    student = Student(id=uuid4(), full_name="Marina", academic_level="ESO")
    student_repo.save(student)

    subject = Subject(id=uuid4(), name="Matemáticas")
    topic = Topic(id=uuid4(), subject_id=subject.id, name="Geometría")
    ex_type = ExerciseType(id=uuid4(), topic_id=topic.id, name="Trigonometría")
    catalog_repo.save_subject(subject)
    catalog_repo.save_topic(topic)
    catalog_repo.save_exercise_type(ex_type)

    session = TutoringSession(
        id=uuid4(),
        student_id=student.id,
        occurred_at=datetime(2026, 11, 16, 17, 30, tzinfo=timezone.utc),
        duration_minutes=75,
        session_notes="Teorema del seno",
        attempts=[
            ExerciseAttempt(
                exercise_type_id=ex_type.id,
                outcome=AttemptOutcome.FAILURE,
                error_cause=ErrorCause.CALCULATION,
                notes="Error al despejar",
            ),
            ExerciseAttempt(
                exercise_type_id=ex_type.id,
                outcome=AttemptOutcome.SUCCESS,
            ),
        ],
    )

    assert session_repo.get_by_id(session.id) is None
    assert session_repo.list_by_student(student.id) == ()

    session_repo.save(session)

    loaded = session_repo.get_by_id(session.id)
    assert loaded is not None
    assert loaded.id == session.id
    assert loaded.student_id == student.id
    assert loaded.duration_minutes == 75
    assert loaded.session_notes == "Teorema del seno"
    assert loaded.failure_rate() == 0.5
    assert len(loaded.attempts) == 2
    assert loaded.attempts[0].outcome == AttemptOutcome.FAILURE
    assert loaded.attempts[0].error_cause == ErrorCause.CALCULATION
    assert loaded.attempts[0].notes == "Error al despejar"
    assert loaded.attempts[1].outcome == AttemptOutcome.SUCCESS

    all_student_sessions = session_repo.list_by_student(student.id)
    assert len(all_student_sessions) == 1
    assert all_student_sessions[0].id == session.id
