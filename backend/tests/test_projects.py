import uuid

import pytest


def unique_email() -> str:
    return f"{uuid.uuid4()}@example.com"


async def create_user_and_get_token(
    client,
    name="Test User",
    password="projectpassword123",
):
    response = await client.post(
        "/auth/register",
        json={
            "name": name,
            "email": unique_email(),
            "password": password,
        },
    )

    assert response.status_code == 201

    data = response.json()

    return data["access_token"]


@pytest.mark.asyncio
async def test_create_project(client):
    token = await create_user_and_get_token(
        client,
        "Project User",
    )

    response = await client.post(
        "/projects/",
        json={
            "title": "My First Project",
            "type": "original",
            "genre": "Fantasy",
            "audience": "Young Adult",
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "My First Project"
    assert data["type"] == "original"


@pytest.mark.asyncio
async def test_list_projects(client):
    token = await create_user_and_get_token(
        client,
        "List User",
    )

    create_response = await client.post(
        "/projects/",
        json={
            "title": "Project One",
            "type": "original",
            "genre": "Sci-Fi",
            "audience": "Adult",
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert create_response.status_code == 201

    response = await client.get(
        "/projects/",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_project_detail(client):
    token = await create_user_and_get_token(
        client,
        "Detail User",
    )

    create_response = await client.post(
        "/projects/",
        json={
            "title": "Detail Project",
            "type": "fanfiction",
            "genre": "Anime",
            "audience": "Teen",
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert create_response.status_code == 201

    project_id = create_response.json()["id"]

    response = await client.get(
        f"/projects/{project_id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == project_id
    assert data["title"] == "Detail Project"


@pytest.mark.asyncio
async def test_update_project(client):
    token = await create_user_and_get_token(
        client,
        "Update User",
    )

    create_response = await client.post(
        "/projects/",
        json={
            "title": "Old Title",
            "type": "original",
            "genre": "Fantasy",
            "audience": "Adult",
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert create_response.status_code == 201

    project_id = create_response.json()["id"]

    response = await client.patch(
        f"/projects/{project_id}",
        json={
            "title": "New Title",
            "status": "in_progress",
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "New Title"
    assert data["status"] == "in_progress"


@pytest.mark.asyncio
async def test_delete_project(client):
    token = await create_user_and_get_token(
        client,
        "Delete User",
    )

    create_response = await client.post(
        "/projects/",
        json={
            "title": "Delete Me",
            "type": "original",
            "genre": "Drama",
            "audience": "Adult",
        },
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert create_response.status_code == 201

    project_id = create_response.json()["id"]

    delete_response = await client.delete(
        f"/projects/{project_id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert delete_response.status_code == 204

    get_response = await client.get(
        f"/projects/{project_id}",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_project_access_denied_for_other_user(client):
    token_a = await create_user_and_get_token(
        client,
        "User A",
    )

    token_b = await create_user_and_get_token(
        client,
        "User B",
    )

    create_response = await client.post(
        "/projects/",
        json={
            "title": "Private Project",
            "type": "original",
            "genre": "Thriller",
            "audience": "Adult",
        },
        headers={
            "Authorization": f"Bearer {token_a}",
        },
    )

    assert create_response.status_code == 201

    project_id = create_response.json()["id"]

    response = await client.get(
        f"/projects/{project_id}",
        headers={
            "Authorization": f"Bearer {token_b}",
        },
    )

    assert response.status_code == 404
