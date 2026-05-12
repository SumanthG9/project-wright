import pytest
from httpx import AsyncClient

# ── Register ──────────────────────────────────────────────────────────────────


async def test_register_success(client: AsyncClient):
    resp = await client.post(
        "/auth/register",
        json={"name": "Alice", "email": "alice@example.com", "password": "password123"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


async def test_register_duplicate_email(client: AsyncClient):
    payload = {"name": "Alice", "email": "alice@example.com", "password": "password123"}
    await client.post("/auth/register", json=payload)
    resp = await client.post("/auth/register", json=payload)
    assert resp.status_code == 409


# ── Login ─────────────────────────────────────────────────────────────────────


async def test_login_success(client: AsyncClient, registered_user: dict):
    resp = await client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "secret123"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


async def test_login_wrong_password(client: AsyncClient, registered_user: dict):
    resp = await client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "wrongpassword"},
    )
    assert resp.status_code == 401


async def test_login_unknown_email(client: AsyncClient):
    resp = await client.post(
        "/auth/login",
        json={"email": "ghost@example.com", "password": "password123"},
    )
    assert resp.status_code == 401


# ── Refresh ───────────────────────────────────────────────────────────────────


async def test_refresh_success(client: AsyncClient, registered_user: dict):
    resp = await client.post(
        "/auth/refresh",
        json={"refresh_token": registered_user["refresh_token"]},
    )
    assert resp.status_code == 200
    assert "access_token" in resp.json()


async def test_refresh_with_access_token_fails(
    client: AsyncClient, registered_user: dict
):
    """Access token must not be accepted at the refresh endpoint."""
    resp = await client.post(
        "/auth/refresh",
        json={"refresh_token": registered_user["access_token"]},
    )
    assert resp.status_code == 401


# ── Me ────────────────────────────────────────────────────────────────────────


async def test_me_success(
    client: AsyncClient, registered_user: dict, auth_headers: dict
):
    resp = await client.get("/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
    assert "hashed_password" not in data  # never leak password hash


async def test_me_no_token(client: AsyncClient):
    resp = await client.get("/auth/me")
    assert resp.status_code == 401


async def test_me_with_refresh_token_fails(client: AsyncClient, registered_user: dict):
    """Refresh token must not grant access to protected routes."""
    headers = {"Authorization": f"Bearer {registered_user['refresh_token']}"}
    resp = await client.get("/auth/me", headers=headers)
    assert resp.status_code == 401


async def test_me_malformed_token(client: AsyncClient):
    headers = {"Authorization": "Bearer this.is.not.a.valid.token"}
    resp = await client.get("/auth/me", headers=headers)
    assert resp.status_code == 401
