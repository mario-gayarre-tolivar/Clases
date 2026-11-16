"""Taxonomic catalog domain entities and snapshot resolver."""

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Protocol, TypeVar
from uuid import UUID

from tutoring.domain.exceptions import DuplicateEntityError, EntityNotFoundError
from tutoring.domain.validation import require_non_empty


class _NamedEntity(Protocol):
    id: UUID
    name: str


_EntityT = TypeVar("_EntityT", bound=_NamedEntity)


@dataclass
class Subject:
    """Academic subject representing the top level of the catalog hierarchy."""

    id: UUID
    name: str
    description: str = ""

    def __post_init__(self) -> None:
        self.name = require_non_empty(self.name, "name")
        self.description = self.description.strip()

    def rename(self, new_name: str) -> None:
        """Rename subject after validating non-empty name."""
        self.name = require_non_empty(new_name, "name")

    def update_description(self, description: str) -> None:
        """Update normalized subject description."""
        self.description = description.strip()


@dataclass
class Topic:
    """Subject topic representing the second level of the catalog hierarchy."""

    id: UUID
    subject_id: UUID
    name: str

    def __post_init__(self) -> None:
        self.name = require_non_empty(self.name, "name")

    def rename(self, new_name: str) -> None:
        """Rename topic after validating non-empty name."""
        self.name = require_non_empty(new_name, "name")


@dataclass
class ExerciseType:
    """Specific exercise category belonging to a topic."""

    id: UUID
    topic_id: UUID
    name: str
    description: str = ""

    def __post_init__(self) -> None:
        self.name = require_non_empty(self.name, "name")
        self.description = self.description.strip()

    def rename(self, new_name: str) -> None:
        """Rename exercise type after validating non-empty name."""
        self.name = require_non_empty(new_name, "name")

    def update_description(self, description: str) -> None:
        """Update normalized exercise type description."""
        self.description = description.strip()


def _index_catalog_items(
    items: Sequence[_EntityT],
    entity_label: str,
    scope_key: Callable[[_EntityT], UUID | None],
    validate_parent: Callable[[_EntityT], object] | None = None,
) -> dict[UUID, _EntityT]:
    """Index entities by ID while enforcing unique IDs, parent links, and scoped names."""
    by_id: dict[UUID, _EntityT] = {}
    seen_names: set[tuple[UUID | None, str]] = set()
    for item in items:
        if item.id in by_id:
            raise DuplicateEntityError(f"Duplicate {entity_label} id '{item.id}'.")
        if validate_parent is not None:
            validate_parent(item)
        name_key = (scope_key(item), item.name.casefold())
        if name_key in seen_names:
            raise DuplicateEntityError(
                f"Duplicate {entity_label} name '{item.name}' in the same scope."
            )
        seen_names.add(name_key)
        by_id[item.id] = item
    return by_id


class AcademicCatalogSnapshot:
    """Consistent, read-only hierarchical view over subjects, topics, and exercise types."""

    def __init__(
        self,
        subjects: Sequence[Subject] = (),
        topics: Sequence[Topic] = (),
        exercise_types: Sequence[ExerciseType] = (),
    ) -> None:
        self._subjects = _index_catalog_items(
            subjects,
            entity_label="subject",
            scope_key=lambda _: None,
        )
        self._topics = _index_catalog_items(
            topics,
            entity_label="topic",
            scope_key=lambda topic: topic.subject_id,
            validate_parent=lambda topic: self.get_subject(topic.subject_id),
        )
        self._exercise_types = _index_catalog_items(
            exercise_types,
            entity_label="exercise_type",
            scope_key=lambda ex: ex.topic_id,
            validate_parent=lambda ex: self.get_topic(ex.topic_id),
        )

    def get_subject(self, subject_id: UUID) -> Subject:
        """Return subject by ID or raise EntityNotFoundError."""
        subject = self._subjects.get(subject_id)
        if subject is None:
            raise EntityNotFoundError(f"Subject '{subject_id}' was not found.")
        return subject

    def get_topic(self, topic_id: UUID) -> Topic:
        """Return topic by ID or raise EntityNotFoundError."""
        topic = self._topics.get(topic_id)
        if topic is None:
            raise EntityNotFoundError(f"Topic '{topic_id}' was not found.")
        return topic

    def get_exercise_type(self, exercise_type_id: UUID) -> ExerciseType:
        """Return exercise type by ID or raise EntityNotFoundError."""
        exercise_type = self._exercise_types.get(exercise_type_id)
        if exercise_type is None:
            raise EntityNotFoundError(
                f"ExerciseType '{exercise_type_id}' was not found."
            )
        return exercise_type

    def resolve_exercise_path(
        self, exercise_type_id: UUID
    ) -> tuple[Subject, Topic, ExerciseType]:
        """Resolve full (Subject, Topic, ExerciseType) tuple for an exercise type."""
        exercise_type = self.get_exercise_type(exercise_type_id)
        topic = self.get_topic(exercise_type.topic_id)
        subject = self.get_subject(topic.subject_id)
        return (subject, topic, exercise_type)

    def topics_for_subject(self, subject_id: UUID) -> tuple[Topic, ...]:
        """Return all topics belonging to a subject."""
        self.get_subject(subject_id)
        return tuple(
            topic for topic in self._topics.values() if topic.subject_id == subject_id
        )

    def exercise_types_for_topic(self, topic_id: UUID) -> tuple[ExerciseType, ...]:
        """Return all exercise types belonging to a topic."""
        self.get_topic(topic_id)
        return tuple(
            ex for ex in self._exercise_types.values() if ex.topic_id == topic_id
        )

    def all_subjects(self) -> tuple[Subject, ...]:
        """Return all subjects in insertion order."""
        return tuple(self._subjects.values())

    def all_topics(self) -> tuple[Topic, ...]:
        """Return all topics in insertion order."""
        return tuple(self._topics.values())

    def all_exercise_types(self) -> tuple[ExerciseType, ...]:
        """Return all exercise types in insertion order."""
        return tuple(self._exercise_types.values())
