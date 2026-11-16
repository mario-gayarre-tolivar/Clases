# Community 1

> 65 nodes · cohesion 0.08

## Key Concepts

- **Subject** (49 connections) — `backend/src/tutoring/domain/entities/catalog.py`
- **ExerciseType** (47 connections) — `backend/src/tutoring/domain/entities/catalog.py`
- **Topic** (47 connections) — `backend/src/tutoring/domain/entities/catalog.py`
- **test_sqlite_session_persistence_lifecycle()** (23 connections) — `backend/tests/integration/test_sqlite_session_repo.py`
- **SqliteCatalogRepository** (20 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_catalog_repo.py`
- **.get_subject()** (16 connections) — `backend/src/tutoring/domain/entities/catalog.py`
- **.resolve_exercise_path()** (16 connections) — `backend/src/tutoring/domain/entities/catalog.py`
- **test_sqlite_catalog_persistence_and_snapshot()** (16 connections) — `backend/tests/integration/test_sqlite_catalog_repo.py`
- **sqlite_catalog_repo.py** (15 connections) — `backend/src/tutoring/infrastructure/persistence/sqlite_catalog_repo.py`
- **test_snapshot_resolves_hierarchy_and_listings()** (14 connections) — `backend/tests/unit/domain/test_catalog_entities.py`
- **test_catalog_entities.py** (13 connections) — `backend/tests/unit/domain/test_catalog_entities.py`
- **.get_topic()** (11 connections) — `backend/src/tutoring/domain/entities/catalog.py`
- **.topics_for_subject()** (10 connections) — `backend/src/tutoring/domain/entities/catalog.py`
- **test_snapshot_raises_not_found_for_unknown_ids()** (10 connections) — `backend/tests/unit/domain/test_catalog_entities.py`
- **.exercise_types_for_topic()** (9 connections) — `backend/src/tutoring/domain/entities/catalog.py`
- **.get_exercise_type()** (9 connections) — `backend/src/tutoring/domain/entities/catalog.py`
- **test_catalog_entities_normalize_and_validate_names()** (9 connections) — `backend/tests/unit/domain/test_catalog_entities.py`
- **test_catalog_entities_reject_blank_rename()** (9 connections) — `backend/tests/unit/domain/test_catalog_entities.py`
- **UUID** (8 connections)
- **.__init__()** (7 connections) — `backend/src/tutoring/domain/entities/catalog.py`
- **test_sqlite_catalog_repo.py** (7 connections) — `backend/tests/integration/test_sqlite_catalog_repo.py`
- **test_snapshot_rejects_duplicate_ids_and_logical_duplicate_names()** (7 connections) — `backend/tests/unit/domain/test_catalog_entities.py`
- **test_snapshot_rejects_orphan_topic_or_exercise_type()** (7 connections) — `backend/tests/unit/domain/test_catalog_entities.py`
- **_index_catalog_items()** (6 connections) — `backend/src/tutoring/domain/entities/catalog.py`
- **.rename()** (6 connections) — `backend/src/tutoring/domain/entities/catalog.py`
- *... and 40 more nodes in this community*

## Relationships

- [Community 13](Community_13.md) (45 shared connections)
- [Community 24](Community_24.md) (21 shared connections)
- [Community 20](Community_20.md) (19 shared connections)
- [Community 8](Community_8.md) (15 shared connections)
- [Community 17](Community_17.md) (14 shared connections)
- [Community 4](Community_4.md) (12 shared connections)
- [Community 5](Community_5.md) (12 shared connections)
- [Community 12](Community_12.md) (10 shared connections)
- [Community 27](Community_27.md) (6 shared connections)
- [Community 25](Community_25.md) (6 shared connections)
- [Community 2](Community_2.md) (5 shared connections)
- [Community 43](Community_43.md) (4 shared connections)

## Source Files

- `backend/src/tutoring/domain/entities/catalog.py`
- `backend/src/tutoring/infrastructure/persistence/sqlite_catalog_repo.py`
- `backend/tests/integration/test_sqlite_catalog_repo.py`
- `backend/tests/integration/test_sqlite_session_repo.py`
- `backend/tests/unit/domain/test_catalog_entities.py`

## Audit Trail

- EXTRACTED: 171 (52%)
- INFERRED: 157 (48%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*