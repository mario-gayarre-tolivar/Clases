"""Unit tests for T3.2: ManageCatalogUseCase."""

from uuid import uuid4

import pytest

from tutoring.application.dtos import (
    CreateExerciseTypeDTO,
    CreateSubjectDTO,
    CreateTopicDTO,
)
from tutoring.application.fakes import InMemoryCatalogRepository
from tutoring.application.use_cases.manage_catalog import ManageCatalogUseCase
from tutoring.domain.exceptions import DuplicateEntityError, EntityNotFoundError, ValidationError


def test_create_catalog_hierarchy_and_retrieve_tree() -> None:
    repo = InMemoryCatalogRepository()
    use_case = ManageCatalogUseCase(catalog_repo=repo)

    subject = use_case.create_subject(CreateSubjectDTO(name="Matemáticas", description="Bach"))
    topic = use_case.create_topic(CreateTopicDTO(subject_id=subject.id, name="Álgebra"))
    ex_type = use_case.create_exercise_type(
        CreateExerciseTypeDTO(topic_id=topic.id, name="Sistemas", description="2x2")
    )

    assert subject.name == "Matemáticas"
    assert topic.name == "Álgebra"
    assert ex_type.name == "Sistemas"

    tree = use_case.get_catalog_tree()
    assert len(tree.subjects) == 1
    assert tree.subjects[0].id == subject.id
    assert len(tree.subjects[0].topics) == 1
    assert tree.subjects[0].topics[0].id == topic.id
    assert len(tree.subjects[0].topics[0].exercise_types) == 1
    assert tree.subjects[0].topics[0].exercise_types[0].id == ex_type.id


def test_create_topic_or_exercise_fails_if_parent_missing() -> None:
    repo = InMemoryCatalogRepository()
    use_case = ManageCatalogUseCase(catalog_repo=repo)

    with pytest.raises(EntityNotFoundError):
        use_case.create_topic(CreateTopicDTO(subject_id=uuid4(), name="Tema huérfano"))

    with pytest.raises(EntityNotFoundError):
        use_case.create_exercise_type(
            CreateExerciseTypeDTO(topic_id=uuid4(), name="Ejercicio huérfano")
        )


def test_create_duplicate_names_in_same_scope_fails() -> None:
    repo = InMemoryCatalogRepository()
    use_case = ManageCatalogUseCase(catalog_repo=repo)

    sub = use_case.create_subject(CreateSubjectDTO(name="Física"))
    with pytest.raises(DuplicateEntityError):
        use_case.create_subject(CreateSubjectDTO(name="  física  "))

    topic = use_case.create_topic(CreateTopicDTO(subject_id=sub.id, name="Óptica"))
    with pytest.raises(DuplicateEntityError):
        use_case.create_topic(CreateTopicDTO(subject_id=sub.id, name="  óptica  "))

    use_case.create_exercise_type(CreateExerciseTypeDTO(topic_id=topic.id, name="Lentes"))
    with pytest.raises(DuplicateEntityError):
        use_case.create_exercise_type(CreateExerciseTypeDTO(topic_id=topic.id, name="lentes"))
