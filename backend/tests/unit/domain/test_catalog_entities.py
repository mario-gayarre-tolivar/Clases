"""Unit tests for T1.2: Subject, Topic, ExerciseType, and AcademicCatalogSnapshot."""

from uuid import uuid4

import pytest

from tutoring.domain.entities.catalog import (
    AcademicCatalogSnapshot,
    ExerciseType,
    Subject,
    Topic,
)
from tutoring.domain.exceptions import (
    DuplicateEntityError,
    EntityNotFoundError,
    ValidationError,
)


def test_catalog_entities_normalize_and_validate_names() -> None:
    subject = Subject(id=uuid4(), name="  Matemáticas  ", description="  ESO  ")
    topic = Topic(id=uuid4(), subject_id=subject.id, name="  Ecuaciones  ")
    exercise = ExerciseType(
        id=uuid4(),
        topic_id=topic.id,
        name="  Primer grado  ",
        description="  Despeje de x  ",
    )

    assert subject.name == "Matemáticas"
    assert subject.description == "ESO"
    assert topic.name == "Ecuaciones"
    assert exercise.name == "Primer grado"
    assert exercise.description == "Despeje de x"

    subject.rename("  Física  ")
    subject.update_description("  Bachillerato  ")
    topic.rename("  Cinemática  ")
    exercise.rename("  MRU  ")
    exercise.update_description("  Velocidad constante  ")

    assert subject.name == "Física"
    assert subject.description == "Bachillerato"
    assert topic.name == "Cinemática"
    assert exercise.name == "MRU"
    assert exercise.description == "Velocidad constante"


def test_catalog_entities_reject_blank_names() -> None:
    with pytest.raises(ValidationError):
        Subject(id=uuid4(), name="   ")
    with pytest.raises(ValidationError):
        Topic(id=uuid4(), subject_id=uuid4(), name="")
    with pytest.raises(ValidationError):
        ExerciseType(id=uuid4(), topic_id=uuid4(), name=" \t ")


def test_catalog_entities_reject_blank_rename() -> None:
    subject = Subject(id=uuid4(), name="Química")
    topic = Topic(id=uuid4(), subject_id=subject.id, name="Estequiometría")
    exercise = ExerciseType(id=uuid4(), topic_id=topic.id, name="Ajuste redox")

    with pytest.raises(ValidationError):
        subject.rename(" ")
    with pytest.raises(ValidationError):
        topic.rename("")
    with pytest.raises(ValidationError):
        exercise.rename("\n")


def test_snapshot_resolves_hierarchy_and_listings() -> None:
    math = Subject(id=uuid4(), name="Matemáticas")
    physics = Subject(id=uuid4(), name="Física")
    algebra = Topic(id=uuid4(), subject_id=math.id, name="Álgebra")
    calculus = Topic(id=uuid4(), subject_id=math.id, name="Cálculo")
    linear_eq = ExerciseType(id=uuid4(), topic_id=algebra.id, name="Ecuación lineal")

    snapshot = AcademicCatalogSnapshot(
        subjects=[math, physics],
        topics=[algebra, calculus],
        exercise_types=[linear_eq],
    )

    assert snapshot.get_subject(math.id) == math
    assert snapshot.get_topic(algebra.id) == algebra
    assert snapshot.get_exercise_type(linear_eq.id) == linear_eq
    assert snapshot.resolve_exercise_path(linear_eq.id) == (math, algebra, linear_eq)
    assert snapshot.topics_for_subject(math.id) == (algebra, calculus)
    assert snapshot.topics_for_subject(physics.id) == ()
    assert snapshot.exercise_types_for_topic(algebra.id) == (linear_eq,)
    assert snapshot.all_subjects() == (math, physics)
    assert snapshot.all_topics() == (algebra, calculus)
    assert snapshot.all_exercise_types() == (linear_eq,)


def test_snapshot_rejects_orphan_topic_or_exercise_type() -> None:
    math = Subject(id=uuid4(), name="Matemáticas")
    orphan_topic = Topic(id=uuid4(), subject_id=uuid4(), name="Geometría")

    with pytest.raises(EntityNotFoundError):
        AcademicCatalogSnapshot(subjects=[math], topics=[orphan_topic])

    valid_topic = Topic(id=uuid4(), subject_id=math.id, name="Álgebra")
    orphan_exercise = ExerciseType(id=uuid4(), topic_id=uuid4(), name="Polinomios")

    with pytest.raises(EntityNotFoundError):
        AcademicCatalogSnapshot(
            subjects=[math],
            topics=[valid_topic],
            exercise_types=[orphan_exercise],
        )


def test_snapshot_rejects_duplicate_ids_and_logical_duplicate_names() -> None:
    dup_id = uuid4()
    with pytest.raises(DuplicateEntityError):
        AcademicCatalogSnapshot(
            subjects=[
                Subject(id=dup_id, name="Matemáticas"),
                Subject(id=dup_id, name="Física"),
            ]
        )

    with pytest.raises(DuplicateEntityError):
        AcademicCatalogSnapshot(
            subjects=[
                Subject(id=uuid4(), name="Matemáticas"),
                Subject(id=uuid4(), name="matemáticas"),
            ]
        )

    math = Subject(id=uuid4(), name="Matemáticas")
    with pytest.raises(DuplicateEntityError):
        AcademicCatalogSnapshot(
            subjects=[math],
            topics=[
                Topic(id=uuid4(), subject_id=math.id, name="Álgebra"),
                Topic(id=uuid4(), subject_id=math.id, name="álgebra"),
            ],
        )

    algebra = Topic(id=uuid4(), subject_id=math.id, name="Álgebra")
    with pytest.raises(DuplicateEntityError):
        AcademicCatalogSnapshot(
            subjects=[math],
            topics=[algebra],
            exercise_types=[
                ExerciseType(id=uuid4(), topic_id=algebra.id, name="Matrices"),
                ExerciseType(id=uuid4(), topic_id=algebra.id, name="MATRICES"),
            ],
        )


def test_snapshot_allows_same_topic_name_under_different_subjects() -> None:
    math = Subject(id=uuid4(), name="Matemáticas")
    physics = Subject(id=uuid4(), name="Física")
    t1 = Topic(id=uuid4(), subject_id=math.id, name="Vectores")
    t2 = Topic(id=uuid4(), subject_id=physics.id, name="Vectores")

    snapshot = AcademicCatalogSnapshot(subjects=[math, physics], topics=[t1, t2])
    assert snapshot.topics_for_subject(math.id) == (t1,)
    assert snapshot.topics_for_subject(physics.id) == (t2,)


def test_snapshot_raises_not_found_for_unknown_ids() -> None:
    snapshot = AcademicCatalogSnapshot()
    missing_id = uuid4()

    with pytest.raises(EntityNotFoundError):
        snapshot.get_subject(missing_id)
    with pytest.raises(EntityNotFoundError):
        snapshot.get_topic(missing_id)
    with pytest.raises(EntityNotFoundError):
        snapshot.get_exercise_type(missing_id)
    with pytest.raises(EntityNotFoundError):
        snapshot.resolve_exercise_path(missing_id)
    with pytest.raises(EntityNotFoundError):
        snapshot.topics_for_subject(missing_id)
    with pytest.raises(EntityNotFoundError):
        snapshot.exercise_types_for_topic(missing_id)
