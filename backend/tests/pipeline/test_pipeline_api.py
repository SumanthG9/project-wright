import uuid

import pytest


def unique_email() -> str:
    return f"pipeline_{uuid.uuid4()}@example.com"


async def create_pipeline_workflow(client):
    register_response = await client.post(
        "/auth/register",
        json={
            "name": "Pipeline User",
            "email": unique_email(),
            "password": "password123",
        },
    )

    tokens = register_response.json()

    headers = {
        "Authorization": f"Bearer {tokens['access_token']}",
    }

    project_response = await client.post(
        "/projects/",
        json={
            "title": "Pipeline Project",
            "type": "original",
            "genre": "Fantasy",
            "audience": "Adult",
        },
        headers=headers,
    )

    project_id = project_response.json()["id"]

    with open("testdata/sample.docx", "rb") as docx_file:
        upload_response = await client.post(
            f"/uploads/{project_id}",
            files={
                "file": (
                    "sample.docx",
                    docx_file,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                ),
            },
            headers=headers,
        )

    assert upload_response.status_code == 201

    response = await client.post(
        "/pipeline/start",
        json={
            "project_id": project_id,
        },
    )

    assert response.status_code == 200

    return response.json()["workflow_id"]


@pytest.mark.asyncio
async def test_start_pipeline(client):
    workflow_id = await create_pipeline_workflow(client)

    assert workflow_id


@pytest.mark.asyncio
async def test_pipeline_status(client):
    workflow_id = await create_pipeline_workflow(client)

    response = await client.get(f"/pipeline/{workflow_id}/status")

    assert response.status_code == 200

    data = response.json()

    assert data["paused"] is True
    assert data["waiting_for_input"] is True


@pytest.mark.asyncio
async def test_pipeline_approve(client):
    workflow_id = await create_pipeline_workflow(client)

    response = await client.post(
        f"/pipeline/{workflow_id}/approve",
        json={},
    )

    assert response.status_code == 200

    status_response = await client.get(f"/pipeline/{workflow_id}/status")

    data = status_response.json()

    assert data["status"] == "completed"
    assert data["approval_status"] == "approved"
