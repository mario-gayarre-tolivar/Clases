"""Integration tests for T4.1: SQLite catalog repository and schema."""

from uuid import uuid4

import pytest

from tutoring.domain.entities.catalog import ExerciseType, Subject, Topic
from tutoring.infrastructure.persistence.sqlite_catalog_repo import (
    SqliteCatalogRepository,
)
from tutoring.infrastructure.persistence.sqlite_db import init_sqlite_db


def test_sqlite_catalog_persistence_and_snapshot() -> None:
    conn = init_sqlite_db(":memory:")
    repo = SqliteCatalogRepository(conn)

    subject = Subject(id=uuid4(), name="Matemáticas", description="Bachillerato")
    topic = Topic(id=uuid4(), subject_id=subject.id, name="Matrices")
    ex_type = ExerciseType(
        id=uuid4(),
        topic_id=topic.id,
        name="Producto",
        description="Multiplicación de matrices",
    )

    assert repo.get_subject(subject.id) is None
    assert repo.get_topic(topic.id) is None
    assert repo.get_exercise_type(ex_type.id) is None

    repo.save_subject(subject)
    repo.save_topic(topic)
    repo.save_exercise_type(ex_type)

    assert repo.get_subject(subject.id) == subject
    assert repo.get_topic(topic.id) == topic
    assert repo.get_exercise_type(ex_type.id) == ex_type

    # Update description / rename
    subject.rename("Matemáticas II")
    repo.save_subject(subject)
    updated_sub = repo.get_subject(subject.id)
    assert updated_sub is not None
    assert updated_sub.name == "Matemáticas II"

    snapshot = repo.get_snapshot()
    assert snapshot.get_subject(subject.id).name == "Matemáticas II"
    assert snapshot.resolve_exercise_path(ex_type.id)[2] == ex_type
