"""SQLite implementation of SessionRepository."""

import sqlite3
from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

from tutoring.domain.entities.session import TutoringSession
from tutoring.domain.enums import AttemptOutcome, ErrorCause
from tutoring.domain.ports.repositories import SessionRepository
from tutoring.domain.value_objects.attempt import ExerciseAttempt


class SqliteSessionRepository(SessionRepository):
    """Persists and queries tutoring sessions and exercise attempts in SQLite."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def save(self, session: TutoringSession) -> None:
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO tutoring_sessions (id, student_id, occurred_at, duration_minutes, session_notes)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    student_id = excluded.student_id,
                    occurred_at = excluded.occurred_at,
                    duration_minutes = excluded.duration_minutes,
                    session_notes = excluded.session_notes;
                """,
                (
                    str(session.id),
                    str(session.student_id),
                    session.occurred_at.isoformat(),
                    session.duration_minutes,
                    session.session_notes,
                ),
            )
            self._conn.execute(
                "DELETE FROM exercise_attempts WHERE session_id = ?;",
                (str(session.id),),
            )
            for attempt in session.attempts:
                self._conn.execute(
                    """
                    INSERT INTO exercise_attempts (session_id, exercise_type_id, outcome, error_cause, notes)
                    VALUES (?, ?, ?, ?, ?);
                    """,
                    (
                        str(session.id),
                        str(attempt.exercise_type_id),
                        attempt.outcome.value,
                        attempt.error_cause.value if attempt.error_cause else None,
                        attempt.notes,
                    ),
                )

    def get_by_id(self, session_id: UUID) -> TutoringSession | None:
        cur = self._conn.execute(
            """
            SELECT id, student_id, occurred_at, duration_minutes, session_notes
            FROM tutoring_sessions
            WHERE id = ?;
            """,
            (str(session_id),),
        )
        row = cur.fetchone()
        if not row:
            return None
        return self._hydrate_session(row)

    def list_by_student(self, student_id: UUID) -> Sequence[TutoringSession]:
        cur = self._conn.execute(
            """
            SELECT id, student_id, occurred_at, duration_minutes, session_notes
            FROM tutoring_sessions
            WHERE student_id = ?
            ORDER BY occurred_at DESC;
            """,
            (str(student_id),),
        )
        rows = cur.fetchall()
        return tuple(self._hydrate_session(row) for row in rows)

    def _hydrate_session(self, row: sqlite3.Row) -> TutoringSession:
        session_id = UUID(row["id"])
        attempts_cur = self._conn.execute(
            """
            SELECT exercise_type_id, outcome, error_cause, notes
            FROM exercise_attempts
            WHERE session_id = ?
            ORDER BY id ASC;
            """,
            (str(session_id),),
        )
        attempt_rows = attempts_cur.fetchall()
        attempts = [
            ExerciseAttempt(
                exercise_type_id=UUID(a_row["exercise_type_id"]),
                outcome=AttemptOutcome(a_row["outcome"]),
                error_cause=ErrorCause(a_row["error_cause"])
                if a_row["error_cause"]
                else None,
                notes=a_row["notes"],
            )
            for a_row in attempt_rows
        ]
        return TutoringSession(
            id=session_id,
            student_id=UUID(row["student_id"]),
            occurred_at=datetime.fromisoformat(row["occurred_at"]),
            duration_minutes=row["duration_minutes"],
            session_notes=row["session_notes"],
            attempts=attempts,
        )
