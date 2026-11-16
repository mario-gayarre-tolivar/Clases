"""Integration tests for T5.1: FastAPI catalog endpoints and DomainError mapping."""

from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from tutoring.presentation.api.app import create_app


@pytest.mark.asyncio
async def test_catalog_api_flow_and_error_handling() -> None:
    app = create_app(":memory:")
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Initially empty tree
        res = await client.get("/api/catalog")
        assert res.status_code == 200
        assert res.json() == {"subjects": []}

        # Create Subject
        res = await client.post(
            "/api/catalog/subjects",
            json={"name": "Matemáticas", "description": "Bachillerato"},
        )
        assert res.status_code == 201
        subject_data = res.json()
        subject_id = subject_data["id"]
        assert subject_data["name"] == "Matemáticas"

        # Duplicate subject returns 409 Conflict
        res_dup = await client.post(
            "/api/catalog/subjects",
            json={"name": "  matemáticas  "},
        )
        assert res_dup.status_code == 409
        assert "detail" in res_dup.json()

        # Create Topic
        res_topic = await client.post(
            "/api/catalog/topics",
            json={"subject_id": subject_id, "name": "Álgebra"},
        )
        assert res_topic.status_code == 201
        topic_id = res_topic.json()["id"]

        # Create topic with invalid subject -> 404 Not Found
        res_orphan_topic = await client.post(
            "/api/catalog/topics",
            json={"subject_id": str(uuid4()), "name": "Geometría"},
        )
        assert res_orphan_topic.status_code == 404

        # Create ExerciseType
        res_ex = await client.post(
            "/api/catalog/exercise-types",
            json={"topic_id": topic_id, "name": "Ecuaciones 2º Grado"},
        )
        assert res_ex.status_code == 201
        assert res_ex.json()["name"] == "Ecuaciones 2º Grado"

        # Blank name returns 422
        res_invalid = await client.post(
            "/api/catalog/subjects",
            json={"name": "   "},
        )
        assert res_invalid.status_code == 422

        # Verify catalog tree populated
        tree_res = await client.get("/api/catalog")
        assert tree_res.status_code == 200
        tree = tree_res.json()
        assert len(tree["subjects"]) == 1
        assert tree["subjects"][0]["name"] == "Matemáticas"
        assert len(tree["subjects"][0]["topics"]) == 1
        assert tree["subjects"][0]["topics"][0]["name"] == "Álgebra"
        assert len(tree["subjects"][0]["topics"][0]["exercise_types"]) == 1
