"""SQLite implementation of StudentRepository."""

import sqlite3
from collections.abc import Sequence
from datetime import date
from uuid import UUID

from tutoring.domain.entities.student import Student
from tutoring.domain.ports.repositories import StudentRepository
from tutoring.domain.value_objects.exam_goal import ExamGoal


class SqliteStudentRepository(StudentRepository):
    """Persists and loads Student aggregates including ExamGoal value objects."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, student: Student) -> None:
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO students (id, full_name, academic_level, pedagogical_notes)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    full_name = excluded.full_name,
                    academic_level = excluded.academic_level,
                    pedagogical_notes = excluded.pedagogical_notes;
                """,
                (
                    str(student.id),
                    student.full_name,
                    student.academic_level,
                    student.pedagogical_notes,
                ),
            )
            # Re-sync exam goals
            self._conn.execute(
                "DELETE FROM exam_goals WHERE student_id = ?;",
                (str(student.id),),
            )
            for goal in student.exam_goals:
                topic_ids_str = ",".join(str(tid) for tid in goal.topic_ids)
                self._conn.execute(
                    """
                    INSERT INTO exam_goals (id, student_id, subject_id, title, exam_date, topic_ids)
                    VALUES (?, ?, ?, ?, ?, ?);
                    """,
                    (
                        str(goal.id),
                        str(student.id),
                        str(goal.subject_id),
                        goal.title,
                        goal.exam_date.isoformat(),
                        topic_ids_str,
                    ),
                )

    def get_by_id(self, student_id: UUID) -> Student | None:
        cur = self._conn.execute(
            "SELECT id, full_name, academic_level, pedagogical_notes FROM students WHERE id = ?;",
            (str(student_id),),
        )
        row = cur.fetchone()
        if not row:
            return None
        return self._hydrate_student(row)

    def list_all(self) -> Sequence[Student]:
        cur = self._conn.execute(
            "SELECT id, full_name, academic_level, pedagogical_notes FROM students ORDER BY full_name ASC;"
        )
        rows = cur.fetchall()
        return tuple(self._hydrate_student(row) for row in rows)

    def delete(self, student_id: UUID) -> bool:
        with self._conn:
            cur = self._conn.execute(
                "DELETE FROM students WHERE id = ?;",
                (str(student_id),),
            )
            return cur.rowcount > 0

    def _hydrate_student(self, row: sqlite3.Row) -> Student:
        student_id = UUID(row["id"])
        goals_cur = self._conn.execute(
            """
            SELECT id, subject_id, title, exam_date, topic_ids
            FROM exam_goals
            WHERE student_id = ?
            ORDER BY exam_date ASC;
            """,
            (str(student_id),),
        )
        goal_rows = goals_cur.fetchall()
        exam_goals: list[ExamGoal] = []
        for g_row in goal_rows:
            raw_topics = g_row["topic_ids"]
            topic_ids = (
                tuple(UUID(t) for t in raw_topics.split(",") if t.strip())
                if raw_topics
                else ()
            )
            exam_goals.append(
                ExamGoal(
                    id=UUID(g_row["id"]),
                    subject_id=UUID(g_row["subject_id"]),
                    title=g_row["title"],
                    exam_date=date.fromisoformat(g_row["exam_date"]),
                    topic_ids=topic_ids,
                )
            )

        return Student(
            id=student_id,
            full_name=row["full_name"],
            academic_level=row["academic_level"],
            pedagogical_notes=row["pedagogical_notes"],
            exam_goals=exam_goals,
        )
