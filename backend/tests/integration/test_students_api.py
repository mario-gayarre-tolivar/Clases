"""Integration tests for T5.2: Student and ExamGoal HTTP endpoints."""

from datetime import date
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from tutoring.presentation.api.app import create_app


@pytest.mark.asyncio
async def test_students_and_exam_goals_api_endpoints() -> None:
    app = create_app(":memory:")
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Create student
            res = await client.post(
                "/api/students",
                json={
                    "full_name": "Valeria Rivas",
                    "academic_level": "2º ESO",
                    "pedagogical_notes": "Rápida en cálculo mental",
                },
            )
            assert res.status_code == 201
            student = res.json()
            student_id = student["id"]
            assert student["full_name"] == "Valeria Rivas"
            assert student["exam_goals"] == []

            # List students
            res_list = await client.get("/api/students")
            assert res_list.status_code == 200
            items = res_list.json()
            assert len(items) == 1
            assert items[0]["id"] == student_id

            # Get detail
            res_detail = await client.get(f"/api/students/{student_id}")
            assert res_detail.status_code == 200
            assert res_detail.json()["id"] == student_id

            # Missing student -> 404
            res_missing = await client.get(f"/api/students/{uuid4()}")
            assert res_missing.status_code == 404

            # Create Subject in catalog for the exam goal
            sub_res = await client.post(
                "/api/catalog/subjects", json={"name": "Biología"}
            )
            subject_id = sub_res.json()["id"]

            # Add ExamGoal
            res_goal = await client.post(
                f"/api/students/{student_id}/exam-goals",
                json={
                    "subject_id": subject_id,
                    "title": "Examen La Célula",
                    "exam_date": "2026-11-25",
                },
            )
            assert res_goal.status_code == 201
            goal = res_goal.json()
            assert goal["title"] == "Examen La Célula"

            # Check detail reflects new goal
            updated_detail = await client.get(f"/api/students/{student_id}")
            assert len(updated_detail.json()["exam_goals"]) == 1
            assert updated_detail.json()["exam_goals"][0]["id"] == goal["id"]
    finally:
        app.state.training_coordinator.shutdown(wait=True)


@pytest.mark.asyncio
async def test_record_exam_goal_result_api_endpoint_and_errors() -> None:
    app = create_app(":memory:")
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            s_res = await client.post("/api/students", json={"full_name": "Inés", "academic_level": "1º Bach"})
            student_id = s_res.json()["id"]
            sub_res = await client.post("/api/catalog/subjects", json={"name": "Química"})
            subject_id = sub_res.json()["id"]
            g_res = await client.post(
                f"/api/students/{student_id}/exam-goals",
                json={"subject_id": subject_id, "title": "Estequiometría", "exam_date": "2026-11-25"},
            )
            goal_id = g_res.json()["id"]

            # Invalid score (> max_score) -> 422
            bad_res = await client.post(
                f"/api/students/{student_id}/exam-goals/{goal_id}/result",
                json={"score": 11.0, "max_score": 10.0},
            )
            assert bad_res.status_code == 422

            # Valid grade -> 201
            ok_res = await client.post(
                f"/api/students/{student_id}/exam-goals/{goal_id}/result",
                json={"score": 4.2, "max_score": 10.0, "notes": "Fallos en moles"},
            )
            assert ok_res.status_code == 201
            body = ok_res.json()
            assert body["result"]["score"] == 4.2
            assert body["result"]["is_passing"] is False

            # Duplicate result -> 409
            dup_res = await client.post(
                f"/api/students/{student_id}/exam-goals/{goal_id}/result",
                json={"score": 7.0},
            )
            assert dup_res.status_code == 409
    finally:
        app.state.training_coordinator.shutdown(wait=True)

