"""End-to-end integration tests for automatic ML training pipeline via FastAPI."""

import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from tutoring.infrastructure.ml.trainer import TrainingReport, TrainingStatus
from tutoring.presentation.api.app import create_app


@pytest.mark.asyncio
async def test_e2e_api_auto_trains_model_and_skips_empty_session_retrain(tmp_path: Path) -> None:
    model_dir = tmp_path / "models"
    db_file = tmp_path / "tutoring.sqlite3"
    app = create_app(
        db_path=str(db_file),
        model_dir=model_dir,
        debounce_seconds=0.05,
        burst_threshold=50,
        min_training_samples=20,
    )
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            sub_id = (await client.post("/api/catalog/subjects", json={"name": "Matemáticas"})).json()["id"]
            top_id = (await client.post("/api/catalog/topics", json={"subject_id": sub_id, "name": "Álgebra"})).json()["id"]
            ex_id = (await client.post("/api/catalog/exercise-types", json={"topic_id": top_id, "name": "Ecuaciones"})).json()["id"]

            # Create 2 students: one passing (target=0), one failing (target=1) across 11 sessions each (>=22 samples)
            s_pass = (await client.post("/api/students", json={"full_name": "Clara", "academic_level": "4º ESO"})).json()["id"]
            s_fail = (await client.post("/api/students", json={"full_name": "Mateo", "academic_level": "4º ESO"})).json()["id"]
            base_dt = datetime(2026, 10, 1, 17, 0, tzinfo=timezone.utc)

            for i in range(11):
                dt = (base_dt + timedelta(days=i)).isoformat()
                await client.post(
                    f"/api/students/{s_pass}/sessions",
                    json={"occurred_at": dt, "duration_minutes": 60, "attempts": [{"exercise_type_id": ex_id, "outcome": "SUCCESS"}]},
                )
                await client.post(
                    f"/api/students/{s_fail}/sessions",
                    json={
                        "occurred_at": dt,
                        "duration_minutes": 60,
                        "attempts": [{"exercise_type_id": ex_id, "outcome": "FAILURE", "error_cause": "CONCEPT"}],
                    },
                )

            # Record exam goals + results (triggers automatic retraining)
            g_fail = (
                await client.post(
                    f"/api/students/{s_fail}/exam-goals",
                    json={"subject_id": sub_id, "title": "Global", "exam_date": "2026-11-20"},
                )
            ).json()["id"]
            await client.post(
                f"/api/students/{s_fail}/exam-goals/{g_fail}/result",
                json={"score": 3.5, "recorded_at": "2026-11-20T18:00:00Z"},
            )

            report = app.state.training_coordinator.flush(timeout=10.0)
            assert report is not None
            assert report.status == TrainingStatus.TRAINED
            assert (model_dir / "active_analyzer.joblib").exists()

            diag_res = await client.get(f"/api/students/{s_fail}/diagnostic")
            assert diag_res.status_code == 200
            assert diag_res.json()["analyzer_name"] == "SklearnPedagogicalAnalyzerV1"

            # Recording a zero-attempt session does not change dataset or trigger retraining
            empty_res = await client.post(
                f"/api/students/{s_pass}/sessions",
                json={"occurred_at": "2026-11-21T17:00:00Z", "duration_minutes": 30, "attempts": []},
            )
            assert empty_res.status_code == 201
            assert app.state.training_coordinator.pending_events == 0

        # Restart app pointing to same DB + model_dir -> lazy-loads persisted model immediately
        app2 = create_app(db_path=str(db_file), model_dir=model_dir)
        try:
            async with AsyncClient(transport=ASGITransport(app=app2), base_url="http://test") as client2:
                diag2 = await client2.get(f"/api/students/{s_fail}/diagnostic")
                assert diag2.status_code == 200
                assert diag2.json()["analyzer_name"] == "SklearnPedagogicalAnalyzerV1"
        finally:
            app2.state.training_coordinator.shutdown(wait=True)
    finally:
        app.state.training_coordinator.shutdown(wait=True)


@pytest.mark.asyncio
async def test_lifespan_shutdown_waits_for_in_flight_training_without_sqlite_errors(
    tmp_path: Path,
) -> None:
    db_file = tmp_path / "tutoring_lifespan.sqlite3"
    app = create_app(
        db_path=str(db_file),
        model_dir=tmp_path / "models",
        debounce_seconds=0.001,
        burst_threshold=1,
    )

    errors: list[Exception] = []
    in_flight_started = threading.Event()
    orig_train = app.state.training_coordinator._trainer.train_and_activate

    def slow_train() -> TrainingReport:
        in_flight_started.set()
        try:
            time.sleep(0.05)
            return orig_train()
        except Exception as exc:
            errors.append(exc)
            raise

    app.state.training_coordinator._trainer.train_and_activate = slow_train

    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            sub = (await client.post("/api/catalog/subjects", json={"name": "Física"})).json()["id"]
            top = (await client.post("/api/catalog/topics", json={"subject_id": sub, "name": "Cinemática"})).json()["id"]
            ex = (await client.post("/api/catalog/exercise-types", json={"topic_id": top, "name": "MRU"})).json()["id"]
            st = (await client.post("/api/students", json={"full_name": "Laura", "academic_level": "1º Bach"})).json()["id"]
            await client.post(
                f"/api/students/{st}/sessions",
                json={
                    "occurred_at": "2026-11-16T10:00:00Z",
                    "duration_minutes": 60,
                    "attempts": [{"exercise_type_id": ex, "outcome": "SUCCESS"}],
                },
            )
        assert in_flight_started.wait(timeout=2.0)

    # With wait=True on shutdown, the in-flight job completes before conn.close().
    # No SQLite ProgrammingError on closed connection occurs.
    time.sleep(0.08)
    assert errors == []


