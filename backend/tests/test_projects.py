import pytest
from httpx import AsyncClient

PROJECT_PAYLOAD = {
    "title": "My Novel",
    "type": "original",
    "genre": "Fantasy",
    "audience": "Adult",
}


# ── Helpers ───────────────────────────────────────────────────────────────────


@pytest.fixture
async def second_user_headers(client: AsyncClient) -> dict:
    resp = await client.post(
        "/auth/register",
        json={"name": "Bob", "email": "bob@example.com", "password": "bobpassword"},
    )
    assert resp.status_code == 201
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def created_project(client: AsyncClient, auth_headers: dict) -> dict:
    resp = await client.post("/projects/", json=PROJECT_PAYLOAD, headers=auth_headers)
    assert resp.status_code == 201
    return resp.json()


# ── Create ────────────────────────────────────────────────────────────────────


async def test_create_project(client: AsyncClient, auth_headers: dict):
    resp = await client.post("/projects/", json=PROJECT_PAYLOAD, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "My Novel"
    assert data["type"] == "original"
    assert data["status"] == "draft"
    assert "id" in data
    assert "created_at" in data


async def test_create_project_unauthenticated(client: AsyncClient):
    resp = await client.post("/projects/", json=PROJECT_PAYLOAD)
    assert resp.status_code == 401


# ── List ──────────────────────────────────────────────────────────────────────


async def test_list_projects(
    client: AsyncClient, auth_headers: dict, created_project: dict
):
    resp = await client.get("/projects/", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == created_project["id"]


async def test_list_projects_only_own(
    client: AsyncClient,
    auth_headers: dict,
    second_user_headers: dict,
    created_project: dict,
):
    """User 2 listing projects must not see User 1's project."""
    resp = await client.get("/projects/", headers=second_user_headers)
    assert resp.status_code == 200
    assert resp.json() == []


# ── Detail ────────────────────────────────────────────────────────────────────


async def test_get_project_detail(
    client: AsyncClient, auth_headers: dict, created_project: dict
):
    project_id = created_project["id"]
    resp = await client.get(f"/projects/{project_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == project_id


async def test_get_project_not_found(client: AsyncClient, auth_headers: dict):
    resp = await client.get("/projects/9999", headers=auth_headers)
    assert resp.status_code == 404


# ── Update ────────────────────────────────────────────────────────────────────


async def test_patch_project(
    client: AsyncClient, auth_headers: dict, created_project: dict
):
    project_id = created_project["id"]
    resp = await client.patch(
        f"/projects/{project_id}",
        json={"title": "Updated Title"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Updated Title"
    assert data["genre"] == "Fantasy"  # unchanged field preserved


# ── Delete ────────────────────────────────────────────────────────────────────


async def test_delete_project(
    client: AsyncClient, auth_headers: dict, created_project: dict
):
    project_id = created_project["id"]
    resp = await client.delete(f"/projects/{project_id}", headers=auth_headers)
    assert resp.status_code == 204

    # Confirm it is gone
    resp = await client.get(f"/projects/{project_id}", headers=auth_headers)
    assert resp.status_code == 404


# ── Ownership enforcement ─────────────────────────────────────────────────────


async def test_ownership_get(
    client: AsyncClient,
    second_user_headers: dict,
    created_project: dict,
):
    project_id = created_project["id"]
    resp = await client.get(f"/projects/{project_id}", headers=second_user_headers)
    assert resp.status_code == 404  # not 403 — resource must not be revealed


async def test_ownership_patch(
    client: AsyncClient,
    second_user_headers: dict,
    created_project: dict,
):
    project_id = created_project["id"]
    resp = await client.patch(
        f"/projects/{project_id}",
        json={"title": "Hijacked"},
        headers=second_user_headers,
    )
    assert resp.status_code == 404


async def test_ownership_delete(
    client: AsyncClient,
    second_user_headers: dict,
    created_project: dict,
):
    project_id = created_project["id"]
    resp = await client.delete(f"/projects/{project_id}", headers=second_user_headers)
    assert resp.status_code == 404
