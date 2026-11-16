"""SQLite implementation of CatalogRepository."""

import sqlite3
from uuid import UUID

from tutoring.domain.entities.catalog import (
    AcademicCatalogSnapshot,
    ExerciseType,
    Subject,
    Topic,
)
from tutoring.domain.ports.repositories import CatalogRepository


class SqliteCatalogRepository(CatalogRepository):
    """Persists and queries catalog items in SQLite."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save_subject(self, subject: Subject) -> None:
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO subjects (id, name, description)
                VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    description = excluded.description;
                """,
                (str(subject.id), subject.name, subject.description),
            )

    def save_topic(self, topic: Topic) -> None:
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO topics (id, subject_id, name)
                VALUES (?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    subject_id = excluded.subject_id,
                    name = excluded.name;
                """,
                (str(topic.id), str(topic.subject_id), topic.name),
            )

    def save_exercise_type(self, exercise_type: ExerciseType) -> None:
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO exercise_types (id, topic_id, name, description)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    topic_id = excluded.topic_id,
                    name = excluded.name,
                    description = excluded.description;
                """,
                (
                    str(exercise_type.id),
                    str(exercise_type.topic_id),
                    exercise_type.name,
                    exercise_type.description,
                ),
            )

    def get_subject(self, subject_id: UUID) -> Subject | None:
        cur = self._conn.execute(
            "SELECT id, name, description FROM subjects WHERE id = ?;",
            (str(subject_id),),
        )
        row = cur.fetchone()
        if not row:
            return None
        return Subject(
            id=UUID(row["id"]),
            name=row["name"],
            description=row["description"],
        )

    def get_topic(self, topic_id: UUID) -> Topic | None:
        cur = self._conn.execute(
            "SELECT id, subject_id, name FROM topics WHERE id = ?;",
            (str(topic_id),),
        )
        row = cur.fetchone()
        if not row:
            return None
        return Topic(
            id=UUID(row["id"]),
            subject_id=UUID(row["subject_id"]),
            name=row["name"],
        )

    def get_exercise_type(self, exercise_type_id: UUID) -> ExerciseType | None:
        cur = self._conn.execute(
            "SELECT id, topic_id, name, description FROM exercise_types WHERE id = ?;",
            (str(exercise_type_id),),
        )
        row = cur.fetchone()
        if not row:
            return None
        return ExerciseType(
            id=UUID(row["id"]),
            topic_id=UUID(row["topic_id"]),
            name=row["name"],
            description=row["description"],
        )

    def get_snapshot(self) -> AcademicCatalogSnapshot:
        subjects_rows = self._conn.execute(
            "SELECT id, name, description FROM subjects ORDER BY name ASC;"
        ).fetchall()
        topics_rows = self._conn.execute(
            "SELECT id, subject_id, name FROM topics ORDER BY name ASC;"
        ).fetchall()
        exercise_rows = self._conn.execute(
            "SELECT id, topic_id, name, description FROM exercise_types ORDER BY name ASC;"
        ).fetchall()

        subjects = [
            Subject(
                id=UUID(row["id"]),
                name=row["name"],
                description=row["description"],
            )
            for row in subjects_rows
        ]
        topics = [
            Topic(
                id=UUID(row["id"]),
                subject_id=UUID(row["subject_id"]),
                name=row["name"],
            )
            for row in topics_rows
        ]
        exercise_types = [
            ExerciseType(
                id=UUID(row["id"]),
                topic_id=UUID(row["topic_id"]),
                name=row["name"],
                description=row["description"],
            )
            for row in exercise_rows
        ]
        return AcademicCatalogSnapshot(
            subjects=subjects,
            topics=topics,
            exercise_types=exercise_types,
        )
