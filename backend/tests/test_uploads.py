from io import BytesIO
from uuid import uuid4

import pytest
from docx import Document
from httpx import AsyncClient


def unique_email() -> str:
    return f"{uuid4().hex}@example.com"


async def create_user_and_token(client: AsyncClient):
    email = unique_email()

    response = await client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": email,
            "password": "testpassword123",
        },
    )

    return response.json()["access_token"]


async def create_project(client: AsyncClient, token: str):
    response = await client.post(
        "/projects/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Project",
            "type": "original",
            "genre": "Fantasy",
            "audience": "Young Adult",
        },
    )

    return response.json()["id"]


def create_docx_bytes(text: str) -> bytes:
    document = Document()

    document.add_paragraph(text)

    buffer = BytesIO()

    document.save(buffer)

    buffer.seek(0)

    return buffer.read()


@pytest.mark.asyncio
async def test_upload_versions_increment(client: AsyncClient):
    token = await create_user_and_token(client)

    project_id = await create_project(client, token)

    file_1 = create_docx_bytes("Version 1")
    file_2 = create_docx_bytes("Version 2")

    response_1 = await client.post(
        f"/uploads/{project_id}",
        headers={"Authorization": f"Bearer {token}"},
        files={
            "file": (
                "draft1.docx",
                file_1,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )

    response_2 = await client.post(
        f"/uploads/{project_id}",
        headers={"Authorization": f"Bearer {token}"},
        files={
            "file": (
                "draft2.docx",
                file_2,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )

    assert response_1.status_code == 201
    assert response_2.status_code == 201

    assert response_1.json()["version"] == 1
    assert response_2.json()["version"] == 2


@pytest.mark.asyncio
async def test_get_latest_draft(client: AsyncClient):
    token = await create_user_and_token(client)

    project_id = await create_project(client, token)

    file_1 = create_docx_bytes("Old Draft")
    file_2 = create_docx_bytes("Latest Draft")

    await client.post(
        f"/uploads/{project_id}",
        headers={"Authorization": f"Bearer {token}"},
        files={
            "file": (
                "old.docx",
                file_1,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )

    await client.post(
        f"/uploads/{project_id}",
        headers={"Authorization": f"Bearer {token}"},
        files={
            "file": (
                "latest.docx",
                file_2,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )

    response = await client.get(
        f"/uploads/{project_id}/latest",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["version"] == 2
    assert "Latest Draft" in response.json()["extracted_text"]


@pytest.mark.asyncio
async def test_list_drafts_ordering(client: AsyncClient):
    token = await create_user_and_token(client)

    project_id = await create_project(client, token)

    for i in range(1, 4):
        file_data = create_docx_bytes(f"Draft {i}")

        await client.post(
            f"/uploads/{project_id}",
            headers={"Authorization": f"Bearer {token}"},
            files={
                "file": (
                    f"draft{i}.docx",
                    file_data,
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            },
        )

    response = await client.get(
        f"/uploads/{project_id}/drafts",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    drafts = response.json()["drafts"]

    assert drafts[0]["version"] == 3
    assert drafts[1]["version"] == 2
    assert drafts[2]["version"] == 1


@pytest.mark.asyncio
async def test_draft_access_denied_for_other_user(client: AsyncClient):
    token_1 = await create_user_and_token(client)
    token_2 = await create_user_and_token(client)

    project_id = await create_project(client, token_1)

    file_data = create_docx_bytes("Private Draft")

    await client.post(
        f"/uploads/{project_id}",
        headers={"Authorization": f"Bearer {token_1}"},
        files={
            "file": (
                "private.docx",
                file_data,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )

    response = await client.get(
        f"/uploads/{project_id}/drafts",
        headers={"Authorization": f"Bearer {token_2}"},
    )

    assert response.status_code == 404
