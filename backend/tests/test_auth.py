import uuid

import pytest


def unique_email() -> str:
    return f"{uuid.uuid4()}@example.com"


@pytest.mark.asyncio
async def test_register_user(client):
    response = await client.post(
        "/auth/register",
        json={
            "name": "Test User",
            "email": unique_email(),
            "password": "strongpassword123",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_user(client):
    email = unique_email()

    register_response = await client.post(
        "/auth/register",
        json={
            "name": "Login User",
            "email": email,
            "password": "mypassword123",
        },
    )

    assert register_response.status_code == 201

    response = await client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "mypassword123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    email = unique_email()

    register_response = await client.post(
        "/auth/register",
        json={
            "name": "Wrong Password User",
            "email": email,
            "password": "correctpassword",
        },
    )

    assert register_response.status_code == 201

    response = await client.post(
        "/auth/login",
        json={
            "email": email,
            "password": "incorrectpassword",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client):
    register_response = await client.post(
        "/auth/register",
        json={
            "name": "Refresh User",
            "email": unique_email(),
            "password": "refreshpassword",
        },
    )

    assert register_response.status_code == 201

    refresh_token = register_response.json()["refresh_token"]

    response = await client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_get_current_user(client):
    email = unique_email()

    register_response = await client.post(
        "/auth/register",
        json={
            "name": "Current User",
            "email": email,
            "password": "currentpassword",
        },
    )

    assert register_response.status_code == 201

    access_token = register_response.json()["access_token"]

    response = await client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Current User"
    assert data["email"] == email


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(client):
    response = await client.get("/auth/me")

    assert response.status_code == 401
