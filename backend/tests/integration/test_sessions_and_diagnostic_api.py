"""Integration tests for T5.3: Session recording and Diagnostic endpoints."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from tutoring.presentation.api.app import create_app


@pytest.mark.asyncio
async def test_session_and_diagnostic_api_endpoints() -> None:
    app = create_app(":memory:")
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create student and catalog hierarchy
        student_res = await client.post(
            "/api/students",
            json={"full_name": "Daniela", "academic_level": "Bachillerato"},
        )
        student_id = student_res.json()["id"]

        sub_res = await client.post(
            "/api/catalog/subjects", json={"name": "Física"}
        )
        sub_id = sub_res.json()["id"]

        top_res = await client.post(
            "/api/catalog/topics",
            json={"subject_id": sub_id, "name": "Dinámica"},
        )
        top_id = top_res.json()["id"]

        ex_res = await client.post(
            "/api/catalog/exercise-types",
            json={"topic_id": top_id, "name": "Plano inclinado"},
        )
        ex_id = ex_res.json()["id"]

        # Record session with 1 failure
        sess_res = await client.post(
            f"/api/students/{student_id}/sessions",
            json={
                "occurred_at": datetime.now(timezone.utc).isoformat(),
                "duration_minutes": 60,
                "session_notes": "Problemas de fricción",
                "attempts": [
                    {
                        "exercise_type_id": ex_id,
                        "outcome": "FAILURE",
                        "error_cause": "CONCEPT",
                        "notes": "No descompone el peso",
                    }
                ],
            },
        )
        assert sess_res.status_code == 201
        session_data = sess_res.json()
        assert session_data["student_id"] == student_id
        assert len(session_data["attempts"]) == 1

        # List sessions
        list_sess_res = await client.get(f"/api/students/{student_id}/sessions")
        assert list_sess_res.status_code == 200
        assert len(list_sess_res.json()) == 1

        # Request diagnostic
        diag_res = await client.get(f"/api/students/{student_id}/diagnostic")
        assert diag_res.status_code == 200
        diagnostic = diag_res.json()
        assert diagnostic["student_id"] == student_id
        assert len(diagnostic["subject_priorities"]) == 1
        assert diagnostic["subject_priorities"][0]["subject_name"] == "Física"
        assert len(diagnostic["weak_exercise_types"]) == 1
        assert diagnostic["weak_exercise_types"][0]["exercise_type_name"] == "Plano inclinado"
