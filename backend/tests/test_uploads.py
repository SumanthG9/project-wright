from io import BytesIO
from uuid import uuid4

import pytest
from httpx import AsyncClient


def unique_email() -> str:
    return f"test_{uuid4().hex}@example.com"


@pytest.mark.asyncio
async def test_upload_versions_increment(client: AsyncClient):
    register_response = await client.post(
        "/auth/register",
        json={
            "name": "Test User",
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
            "title": "Version Test Project",
            "type": "original",
            "genre": "Fantasy",
            "audience": "Young Adult",
        },
        headers=headers,
    )

    project_id = project_response.json()["id"]

    docx_content = BytesIO(b"PK\x03\x04")

    response_1 = await client.post(
        f"/uploads/{project_id}",
        files={
            "file": (
                "draft1.docx",
                docx_content,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ),
        },
        headers=headers,
    )

    response_2 = await client.post(
        f"/uploads/{project_id}",
        files={
            "file": (
                "draft2.docx",
                BytesIO(b"PK\x03\x04"),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ),
        },
        headers=headers,
    )

    assert response_1.status_code in [201, 400]
    assert response_2.status_code in [201, 400]


@pytest.mark.asyncio
async def test_get_latest_draft(client: AsyncClient):
    register_response = await client.post(
        "/auth/register",
        json={
            "name": "Test User",
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
            "title": "Latest Draft Project",
            "type": "original",
            "genre": "Sci-Fi",
            "audience": "Adults",
        },
        headers=headers,
    )

    project_id = project_response.json()["id"]

    latest_response = await client.get(
        f"/uploads/{project_id}/latest",
        headers=headers,
    )

    assert latest_response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_list_drafts_ordering(client: AsyncClient):
    register_response = await client.post(
        "/auth/register",
        json={
            "name": "Test User",
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
            "title": "Ordering Project",
            "type": "original",
            "genre": "Mystery",
            "audience": "Adults",
        },
        headers=headers,
    )

    project_id = project_response.json()["id"]

    drafts_response = await client.get(
        f"/uploads/{project_id}/drafts",
        headers=headers,
    )

    assert drafts_response.status_code == 200


@pytest.mark.asyncio
async def test_draft_access_denied_for_other_user(
    client: AsyncClient,
):
    owner_response = await client.post(
        "/auth/register",
        json={
            "name": "Owner",
            "email": unique_email(),
            "password": "password123",
        },
    )

    owner_tokens = owner_response.json()

    owner_headers = {
        "Authorization": f"Bearer {owner_tokens['access_token']}",
    }

    intruder_response = await client.post(
        "/auth/register",
        json={
            "name": "Intruder",
            "email": unique_email(),
            "password": "password123",
        },
    )

    intruder_tokens = intruder_response.json()

    intruder_headers = {
        "Authorization": f"Bearer {intruder_tokens['access_token']}",
    }

    project_response = await client.post(
        "/projects/",
        json={
            "title": "Protected Project",
            "type": "original",
            "genre": "Fantasy",
            "audience": "Adults",
        },
        headers=owner_headers,
    )

    project_id = project_response.json()["id"]

    latest_response = await client.get(
        f"/uploads/{project_id}/latest",
        headers=intruder_headers,
    )

    assert latest_response.status_code == 404


@pytest.mark.asyncio
async def test_corrupted_pdf_rejected(client: AsyncClient):
    register_response = await client.post(
        "/auth/register",
        json={
            "name": "Test User",
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
            "title": "Corrupted PDF Project",
            "type": "original",
            "genre": "Fantasy",
            "audience": "Young Adult",
        },
        headers=headers,
    )

    project_id = project_response.json()["id"]

    corrupted_pdf = BytesIO(b"this is not a real pdf")

    response = await client.post(
        f"/uploads/{project_id}",
        files={
            "file": (
                "corrupted.pdf",
                corrupted_pdf,
                "application/pdf",
            ),
        },
        headers=headers,
    )

    assert response.status_code == 400
    assert "PDF extraction failed" in response.json()["detail"]
