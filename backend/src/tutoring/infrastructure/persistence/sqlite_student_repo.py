"""SQLite implementation of StudentRepository."""

import contextlib
import sqlite3
import threading
from collections.abc import Sequence
from datetime import date, datetime
from uuid import UUID

from tutoring.domain.entities.student import Student
from tutoring.domain.ports.repositories import StudentRepository
from tutoring.domain.value_objects.exam_goal import ExamGoal, ExamResult


class SqliteStudentRepository(StudentRepository):
    """Persists and loads Student aggregates including ExamGoal value objects."""

    def __init__(
        self, conn: sqlite3.Connection, lock: threading.RLock | None = None
    ) -> None:
        self._conn = conn
        self._lock = lock

    def save(self, student: Student) -> None:
        with self._lock if self._lock is not None else contextlib.nullcontext():
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
                    if goal.result is not None:
                        self._conn.execute(
                            """
                            INSERT INTO exam_results (goal_id, score, max_score, recorded_at, notes)
                            VALUES (?, ?, ?, ?, ?);
                            """,
                            (
                                str(goal.id),
                                goal.result.score,
                                goal.result.max_score,
                                goal.result.recorded_at.isoformat(),
                                goal.result.notes,
                            ),
                        )

    def get_by_id(self, student_id: UUID) -> Student | None:
        with self._lock if self._lock is not None else contextlib.nullcontext():
            cur = self._conn.execute(
                "SELECT id, full_name, academic_level, pedagogical_notes FROM students WHERE id = ?;",
                (str(student_id),),
            )
            row = cur.fetchone()
            if not row:
                return None
            return self._hydrate_student(row)

    def list_all(self) -> Sequence[Student]:
        with self._lock if self._lock is not None else contextlib.nullcontext():
            cur = self._conn.execute(
                "SELECT id, full_name, academic_level, pedagogical_notes FROM students ORDER BY full_name ASC;"
            )
            rows = cur.fetchall()
            return tuple(self._hydrate_student(row) for row in rows)

    def delete(self, student_id: UUID) -> bool:
        with self._lock if self._lock is not None else contextlib.nullcontext():
            with self._conn:
                cur = self._conn.execute(
                    "DELETE FROM students WHERE id = ?;",
                    (str(student_id),),
                )
                return cur.rowcount > 0

    def _hydrate_student(self, row: sqlite3.Row) -> Student:
        with self._lock if self._lock is not None else contextlib.nullcontext():
            student_id = UUID(row["id"])
            goals_cur = self._conn.execute(
                """
                SELECT
                    eg.id,
                    eg.subject_id,
                    eg.title,
                    eg.exam_date,
                    eg.topic_ids,
                    er.score,
                    er.max_score,
                    er.recorded_at,
                    er.notes AS result_notes
                FROM exam_goals eg
                LEFT JOIN exam_results er ON eg.id = er.goal_id
                WHERE eg.student_id = ?
                ORDER BY eg.exam_date ASC;
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
                result: ExamResult | None = None
                if g_row["score"] is not None:
                    result = ExamResult(
                        score=float(g_row["score"]),
                        max_score=float(g_row["max_score"]),
                        recorded_at=datetime.fromisoformat(g_row["recorded_at"]),
                        notes=g_row["result_notes"] or "",
                    )
                exam_goals.append(
                    ExamGoal(
                        id=UUID(g_row["id"]),
                        subject_id=UUID(g_row["subject_id"]),
                        title=g_row["title"],
                        exam_date=date.fromisoformat(g_row["exam_date"]),
                        topic_ids=topic_ids,
                        result=result,
                    )
                )

            return Student(
                id=student_id,
                full_name=row["full_name"],
                academic_level=row["academic_level"],
                pedagogical_notes=row["pedagogical_notes"],
                exam_goals=exam_goals,
            )
