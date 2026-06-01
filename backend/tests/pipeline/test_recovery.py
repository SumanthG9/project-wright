import pytest


@pytest.mark.asyncio
async def test_pipeline_events(client):

    response = await client.post(
        "/pipeline/start",
        json={
            "project_id": 1,
            "draft_id": 1,
        },
    )

    workflow_id = response.json()["workflow_id"]

    events_response = await client.get(f"/pipeline/{workflow_id}/events")

    assert events_response.status_code == 200

    data = events_response.json()

    assert len(data["events"]) >= 4


@pytest.mark.asyncio
async def test_pipeline_history(client):

    response = await client.post(
        "/pipeline/start",
        json={
            "project_id": 1,
            "draft_id": 1,
        },
    )

    workflow_id = response.json()["workflow_id"]

    history_response = await client.get(f"/pipeline/{workflow_id}/history")

    assert history_response.status_code == 200

    data = history_response.json()

    assert data["project_id"] == 1
    assert data["paused"] is True


@pytest.mark.asyncio
async def test_pipeline_resume(client):

    response = await client.post(
        "/pipeline/start",
        json={
            "project_id": 1,
            "draft_id": 1,
        },
    )

    workflow_id = response.json()["workflow_id"]

    resume_response = await client.post(f"/pipeline/{workflow_id}/resume")

    assert resume_response.status_code == 200

    status_response = await client.get(f"/pipeline/{workflow_id}/status")

    data = status_response.json()

    assert data["status"] == "running"
    assert data["paused"] is False
    assert data["waiting_for_input"] is False


@pytest.mark.asyncio
async def test_pipeline_events_not_found(client):

    response = await client.get("/pipeline/does-not-exist/events")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_pipeline_history_not_found(client):

    response = await client.get("/pipeline/does-not-exist/history")

    assert response.status_code == 404
