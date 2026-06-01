import pytest


@pytest.mark.asyncio
async def test_start_pipeline(client):

    response = await client.post(
        "/pipeline/start",
        json={
            "project_id": 1,
            "draft_id": 1,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "workflow_id" in data
    assert data["status"] == "paused"


@pytest.mark.asyncio
async def test_pipeline_status(client):

    response = await client.post(
        "/pipeline/start",
        json={
            "project_id": 1,
            "draft_id": 1,
        },
    )

    workflow_id = response.json()["workflow_id"]

    status_response = await client.get(f"/pipeline/{workflow_id}/status")

    assert status_response.status_code == 200

    data = status_response.json()

    assert data["paused"] is True
    assert data["waiting_for_input"] is True


@pytest.mark.asyncio
async def test_pipeline_approve(client):

    response = await client.post(
        "/pipeline/start",
        json={
            "project_id": 1,
            "draft_id": 1,
        },
    )

    workflow_id = response.json()["workflow_id"]

    approve_response = await client.post(
        f"/pipeline/{workflow_id}/approve",
        json={},
    )

    assert approve_response.status_code == 200

    status_response = await client.get(f"/pipeline/{workflow_id}/status")

    data = status_response.json()

    assert data["status"] == "completed"
    assert data["approval_status"] == "approved"
