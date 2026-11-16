"""Use cases for managing the taxonomic academic catalog."""

from uuid import UUID, uuid4

from tutoring.application.dtos import (
    CatalogTreeDTO,
    CatalogTreeSubjectDTO,
    CatalogTreeTopicDTO,
    CreateExerciseTypeDTO,
    CreateSubjectDTO,
    CreateTopicDTO,
    ExerciseTypeDTO,
    SubjectDTO,
    TopicDTO,
)
from tutoring.domain.entities.catalog import ExerciseType, Subject, Topic
from tutoring.domain.exceptions import DuplicateEntityError, EntityNotFoundError
from tutoring.domain.ports.repositories import CatalogRepository


class ManageCatalogUseCase:
    """Orchestrates creation and queries over subjects, topics, and exercise types."""

    def __init__(self, catalog_repo: CatalogRepository) -> None:
        self._catalog_repo = catalog_repo

    def create_subject(self, dto: CreateSubjectDTO) -> SubjectDTO:
        snapshot = self._catalog_repo.get_snapshot()
        normalized_name = dto.name.strip().casefold()
        for sub in snapshot.all_subjects():
            if sub.name.casefold() == normalized_name:
                raise DuplicateEntityError(f"Subject '{dto.name}' already exists.")

        subject = Subject(id=uuid4(), name=dto.name, description=dto.description)
        self._catalog_repo.save_subject(subject)
        return SubjectDTO(id=subject.id, name=subject.name, description=subject.description)

    def create_topic(self, dto: CreateTopicDTO) -> TopicDTO:
        snapshot = self._catalog_repo.get_snapshot()
        # Ensure subject exists
        snapshot.get_subject(dto.subject_id)

        normalized_name = dto.name.strip().casefold()
        for topic_item in snapshot.topics_for_subject(dto.subject_id):
            if topic_item.name.casefold() == normalized_name:
                raise DuplicateEntityError(
                    f"Topic '{dto.name}' already exists under subject '{dto.subject_id}'."
                )

        topic = Topic(id=uuid4(), subject_id=dto.subject_id, name=dto.name)
        self._catalog_repo.save_topic(topic)
        return TopicDTO(id=topic.id, subject_id=topic.subject_id, name=topic.name)

    def create_exercise_type(self, dto: CreateExerciseTypeDTO) -> ExerciseTypeDTO:
        snapshot = self._catalog_repo.get_snapshot()
        # Ensure topic exists
        snapshot.get_topic(dto.topic_id)

        normalized_name = dto.name.strip().casefold()
        for ex_item in snapshot.exercise_types_for_topic(dto.topic_id):
            if ex_item.name.casefold() == normalized_name:
                raise DuplicateEntityError(
                    f"ExerciseType '{dto.name}' already exists under topic '{dto.topic_id}'."
                )

        ex_type = ExerciseType(
            id=uuid4(),
            topic_id=dto.topic_id,
            name=dto.name,
            description=dto.description,
        )
        self._catalog_repo.save_exercise_type(ex_type)
        return ExerciseTypeDTO(
            id=ex_type.id,
            topic_id=ex_type.topic_id,
            name=ex_type.name,
            description=ex_type.description,
        )

    def get_catalog_tree(self) -> CatalogTreeDTO:
        snapshot = self._catalog_repo.get_snapshot()
        subject_trees: list[CatalogTreeSubjectDTO] = []

        for sub in snapshot.all_subjects():
            topics = snapshot.topics_for_subject(sub.id)
            topic_trees: list[CatalogTreeTopicDTO] = []
            for top in topics:
                exercises = snapshot.exercise_types_for_topic(top.id)
                exercise_dtos = tuple(
                    ExerciseTypeDTO(
                        id=ex.id,
                        topic_id=ex.topic_id,
                        name=ex.name,
                        description=ex.description,
                    )
                    for ex in exercises
                )
                topic_trees.append(
                    CatalogTreeTopicDTO(
                        id=top.id,
                        name=top.name,
                        exercise_types=exercise_dtos,
                    )
                )
            subject_trees.append(
                CatalogTreeSubjectDTO(
                    id=sub.id,
                    name=sub.name,
                    description=sub.description,
                    topics=tuple(topic_trees),
                )
            )

        return CatalogTreeDTO(subjects=tuple(subject_trees))
