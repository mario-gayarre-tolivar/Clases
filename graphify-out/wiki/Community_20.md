# Community 20

> 29 nodes · cohesion 0.21

## Key Concepts

- **dtos.py** (40 connections) — `backend/src/tutoring/application/dtos.py`
- **ManageCatalogUseCase** (26 connections) — `backend/src/tutoring/application/use_cases/manage_catalog.py`
- **manage_catalog.py** (24 connections) — `backend/src/tutoring/application/use_cases/manage_catalog.py`
- **DuplicateEntityError** (18 connections) — `backend/src/tutoring/domain/exceptions.py`
- **.create_exercise_type()** (12 connections) — `backend/src/tutoring/application/use_cases/manage_catalog.py`
- **.create_topic()** (12 connections) — `backend/src/tutoring/application/use_cases/manage_catalog.py`
- **test_create_duplicate_names_in_same_scope_fails()** (11 connections) — `backend/tests/unit/application/test_manage_catalog.py`
- **CreateExerciseTypeDTO** (10 connections) — `backend/src/tutoring/application/dtos.py`
- **CreateTopicDTO** (10 connections) — `backend/src/tutoring/application/dtos.py`
- **.create_subject()** (10 connections) — `backend/src/tutoring/application/use_cases/manage_catalog.py`
- **.get_catalog_tree()** (10 connections) — `backend/src/tutoring/application/use_cases/manage_catalog.py`
- **test_manage_catalog.py** (10 connections) — `backend/tests/unit/application/test_manage_catalog.py`
- **test_create_catalog_hierarchy_and_retrieve_tree()** (10 connections) — `backend/tests/unit/application/test_manage_catalog.py`
- **CreateSubjectDTO** (9 connections) — `backend/src/tutoring/application/dtos.py`
- **test_create_topic_or_exercise_fails_if_parent_missing()** (9 connections) — `backend/tests/unit/application/test_manage_catalog.py`
- **.get_snapshot()** (8 connections) — `backend/src/tutoring/domain/ports/repositories.py`
- **ExerciseTypeDTO** (7 connections) — `backend/src/tutoring/application/dtos.py`
- **CatalogTreeDTO** (6 connections) — `backend/src/tutoring/application/dtos.py`
- **SubjectDTO** (6 connections) — `backend/src/tutoring/application/dtos.py`
- **TopicDTO** (6 connections) — `backend/src/tutoring/application/dtos.py`
- **.all_subjects()** (6 connections) — `backend/src/tutoring/domain/entities/catalog.py`
- **CatalogTreeSubjectDTO** (4 connections) — `backend/src/tutoring/application/dtos.py`
- **CatalogTreeTopicDTO** (4 connections) — `backend/src/tutoring/application/dtos.py`
- **Application Data Transfer Objects.** (1 connections) — `backend/src/tutoring/application/dtos.py`
- **Use cases for managing the taxonomic academic catalog.** (1 connections) — `backend/src/tutoring/application/use_cases/manage_catalog.py`
- *... and 4 more nodes in this community*

## Relationships

- [Community 1](Community_1.md) (19 shared connections)
- [Community 8](Community_8.md) (14 shared connections)
- [Community 4](Community_4.md) (13 shared connections)
- [Community 25](Community_25.md) (12 shared connections)
- [Community 28](Community_28.md) (12 shared connections)
- [Community 5](Community_5.md) (11 shared connections)
- [Community 27](Community_27.md) (8 shared connections)
- [Community 24](Community_24.md) (6 shared connections)
- [Community 13](Community_13.md) (3 shared connections)
- [Community 17](Community_17.md) (2 shared connections)
- [Community 2](Community_2.md) (1 shared connections)
- [Community 12](Community_12.md) (1 shared connections)

## Source Files

- `backend/src/tutoring/application/dtos.py`
- `backend/src/tutoring/application/use_cases/manage_catalog.py`
- `backend/src/tutoring/domain/entities/catalog.py`
- `backend/src/tutoring/domain/exceptions.py`
- `backend/src/tutoring/domain/ports/repositories.py`
- `backend/tests/unit/application/test_manage_catalog.py`

## Audit Trail

- EXTRACTED: 123 (65%)
- INFERRED: 65 (35%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*