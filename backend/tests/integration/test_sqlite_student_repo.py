"""Integration tests for T4.2: SQLite student repository."""

import threading
from datetime import date, datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest

from tutoring.domain.entities.catalog import Subject
from tutoring.domain.entities.student import Student
from tutoring.domain.value_objects.exam_goal import ExamGoal, ExamResult
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


def test_sqlite_persists_exam_goal_result_roundtrip() -> None:
    conn = init_sqlite_db(":memory:")
    catalog_repo = SqliteCatalogRepository(conn)
    student_repo = SqliteStudentRepository(conn)

    subject = Subject(id=uuid4(), name="Matemáticas")
    catalog_repo.save_subject(subject)
    student = Student(id=uuid4(), full_name="Nora", academic_level="4º ESO")
    goal = ExamGoal(id=uuid4(), subject_id=subject.id, title="Funciones", exam_date=date(2026, 11, 20))
    student.add_exam_goal(goal, today=date(2026, 11, 16))
    result = ExamResult(
        score=7.25,
        max_score=10.0,
        recorded_at=datetime(2026, 11, 20, 18, 0, tzinfo=timezone.utc),
        notes="Muy bien en gráficas",
    )
    student.record_exam_result(goal.id, result)
    student_repo.save(student)

    loaded = student_repo.get_by_id(student.id)
    assert loaded is not None
    assert loaded.exam_goals[0].result == result


def test_sqlite_repositories_safe_under_concurrent_thread_access() -> None:
    conn = init_sqlite_db(":memory:")
    db_lock = threading.RLock()
    catalog_repo = SqliteCatalogRepository(conn, lock=db_lock)
    student_repo = SqliteStudentRepository(conn, lock=db_lock)

    subject = Subject(id=uuid4(), name="Física")
    catalog_repo.save_subject(subject)
    errors: list[Exception] = []

    def writer() -> None:
        try:
            for i in range(40):
                s = Student(id=uuid4(), full_name=f"Alumno {i}", academic_level="1º Bach")
                student_repo.save(s)
        except Exception as exc:  # pragma: no cover
            errors.append(exc)

    def reader() -> None:
        try:
            for _ in range(40):
                student_repo.list_all()
                catalog_repo.get_snapshot()
        except Exception as exc:  # pragma: no cover
            errors.append(exc)

    t1 = threading.Thread(target=writer)
    t2 = threading.Thread(target=reader)
    t1.start()
    t2.start()
    t1.join(timeout=5)
    t2.join(timeout=5)
    assert errors == []
    assert len(student_repo.list_all()) == 40


def test_sqlite_db_wal_mode_and_busy_timeout_for_file_backed(tmp_path: Path) -> None:
    db_file = tmp_path / "test.db"
    conn = init_sqlite_db(db_file)
    cur = conn.execute("PRAGMA journal_mode;")
    mode = cur.fetchone()[0]
    assert mode.lower() == "wal"
    cur = conn.execute("PRAGMA busy_timeout;")
    timeout = cur.fetchone()[0]
    assert timeout == 5000
    conn.close()
