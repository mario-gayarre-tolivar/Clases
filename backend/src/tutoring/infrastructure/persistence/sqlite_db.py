"""SQLite database connection and schema initialization."""

import sqlite3
from pathlib import Path

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS subjects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS topics (
    id TEXT PRIMARY KEY,
    subject_id TEXT NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS exercise_types (
    id TEXT PRIMARY KEY,
    topic_id TEXT NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS students (
    id TEXT PRIMARY KEY,
    full_name TEXT NOT NULL,
    academic_level TEXT NOT NULL,
    pedagogical_notes TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS exam_goals (
    id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    subject_id TEXT NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    exam_date TEXT NOT NULL,
    topic_ids TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS tutoring_sessions (
    id TEXT PRIMARY KEY,
    student_id TEXT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    occurred_at TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL,
    session_notes TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS exercise_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES tutoring_sessions(id) ON DELETE CASCADE,
    exercise_type_id TEXT NOT NULL REFERENCES exercise_types(id) ON DELETE CASCADE,
    outcome TEXT NOT NULL,
    error_cause TEXT,
    notes TEXT NOT NULL DEFAULT ''
);
"""


def init_sqlite_db(db_path: str | Path = ":memory:") -> sqlite3.Connection:
    """Create SQLite database connection and initialize tables."""
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(SCHEMA_SQL)
    conn.row_factory = sqlite3.Row
    return conn
