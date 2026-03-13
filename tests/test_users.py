"""Tests for user API endpoints."""

import pytest
from httpx import AsyncClient


class TestCreateUser:
    """Tests for POST /api/v1/users."""

    async def test_create_user_success(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/users",
            json={"email": "alice@example.com", "name": "Alice"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "alice@example.com"
        assert data["name"] == "Alice"
        assert "id" in data
        assert "created_at" in data

    async def test_create_user_duplicate_email(self, async_client: AsyncClient):
        await async_client.post(
            "/api/v1/users",
            json={"email": "bob@example.com", "name": "Bob"},
        )
        response = await async_client.post(
            "/api/v1/users",
            json={"email": "bob@example.com", "name": "Bob2"},
        )
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    async def test_create_user_missing_fields(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/users",
            json={"email": "noname@example.com"},
        )
        assert response.status_code == 422


class TestGetUser:
    """Tests for GET /api/v1/users/{user_id}."""

    async def test_get_user_success(self, async_client: AsyncClient):
        create_resp = await async_client.post(
            "/api/v1/users",
            json={"email": "charlie@example.com", "name": "Charlie"},
        )
        user_id = create_resp.json()["id"]

        response = await async_client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 200
        assert response.json()["email"] == "charlie@example.com"

    async def test_get_user_not_found(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/users/9999")
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]


class TestListUsers:
    """Tests for GET /api/v1/users."""

    async def test_list_users_empty(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/users")
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_users_with_data(self, async_client: AsyncClient):
        await async_client.post(
            "/api/v1/users",
            json={"email": "d@example.com", "name": "D"},
        )
        await async_client.post(
            "/api/v1/users",
            json={"email": "e@example.com", "name": "E"},
        )
        response = await async_client.get("/api/v1/users")
        assert response.status_code == 200
        assert len(response.json()) == 2
