"""ASGI entrypoint for running the tutoring API with Uvicorn."""

import os

from tutoring.presentation.api.app import create_app

app = create_app(db_path=os.getenv("TUTORING_DB_PATH", "tutoring.sqlite3"))
