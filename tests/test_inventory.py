"""Tests for inventory API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.fixture
async def product_with_inventory(async_client: AsyncClient) -> dict:
    """Create a product (which auto-creates inventory) and set inventory quantity."""
    # Create a category
    cat_resp = await async_client.post(
        "/api/v1/categories", json={"name": "Test Category"}
    )
    assert cat_resp.status_code == 201
    category_id = cat_resp.json()["id"]

    # Create a product (auto-creates inventory with quantity=0)
    prod_resp = await async_client.post(
        "/api/v1/products",
        json={
            "name": "Test Product",
            "price": 25.00,
            "category_id": category_id,
        },
    )
    assert prod_resp.status_code == 201
    product_id = prod_resp.json()["id"]

    # Set inventory to 100
    inv_resp = await async_client.put(
        f"/api/v1/inventory/{product_id}", json={"quantity": 100}
    )
    assert inv_resp.status_code == 200

    return {"product_id": product_id, "category_id": category_id}


class TestGetInventory:
    """Tests for GET /api/v1/inventory/{product_id}."""

    async def test_get_inventory_success(
        self, async_client: AsyncClient, product_with_inventory: dict
    ):
        product_id = product_with_inventory["product_id"]
        response = await async_client.get(f"/api/v1/inventory/{product_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["product_id"] == product_id
        assert data["quantity"] == 100
        assert data["reserved"] == 0
        assert "last_updated" in data

    async def test_get_inventory_not_found(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/inventory/9999")
        assert response.status_code == 404
        assert "Inventory not found" in response.json()["detail"]


class TestUpdateInventory:
    """Tests for PUT /api/v1/inventory/{product_id}."""

    async def test_update_inventory_success(
        self, async_client: AsyncClient, product_with_inventory: dict
    ):
        product_id = product_with_inventory["product_id"]
        response = await async_client.put(
            f"/api/v1/inventory/{product_id}", json={"quantity": 200}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 200
        assert data["reserved"] == 0

    async def test_update_inventory_not_found(self, async_client: AsyncClient):
        response = await async_client.put(
            "/api/v1/inventory/9999", json={"quantity": 50}
        )
        assert response.status_code == 404

    async def test_update_inventory_invalid_body(self, async_client: AsyncClient):
        response = await async_client.put(
            "/api/v1/inventory/1", json={"quantity": "not_a_number"}
        )
        assert response.status_code == 422


class TestReserveInventory:
    """Tests for POST /api/v1/inventory/{product_id}/reserve."""

    async def test_reserve_inventory_success(
        self, async_client: AsyncClient, product_with_inventory: dict
    ):
        product_id = product_with_inventory["product_id"]
        response = await async_client.post(
            f"/api/v1/inventory/{product_id}/reserve", json={"quantity": 30}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 100
        assert data["reserved"] == 30

    async def test_reserve_inventory_multiple_reservations(
        self, async_client: AsyncClient, product_with_inventory: dict
    ):
        product_id = product_with_inventory["product_id"]

        # First reservation
        resp1 = await async_client.post(
            f"/api/v1/inventory/{product_id}/reserve", json={"quantity": 40}
        )
        assert resp1.status_code == 200
        assert resp1.json()["reserved"] == 40

        # Second reservation
        resp2 = await async_client.post(
            f"/api/v1/inventory/{product_id}/reserve", json={"quantity": 30}
        )
        assert resp2.status_code == 200
        assert resp2.json()["reserved"] == 70

    async def test_reserve_inventory_insufficient(
        self, async_client: AsyncClient, product_with_inventory: dict
    ):
        product_id = product_with_inventory["product_id"]
        response = await async_client.post(
            f"/api/v1/inventory/{product_id}/reserve", json={"quantity": 150}
        )

        assert response.status_code == 400
        assert "Insufficient inventory" in response.json()["detail"]

    async def test_reserve_inventory_not_found(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/inventory/9999/reserve", json={"quantity": 5}
        )
        assert response.status_code == 404

    async def test_reserve_inventory_arithmetic(
        self, async_client: AsyncClient, product_with_inventory: dict
    ):
        """Test that reservation correctly tracks available = quantity - reserved."""
        product_id = product_with_inventory["product_id"]

        # Reserve 80 out of 100
        await async_client.post(
            f"/api/v1/inventory/{product_id}/reserve", json={"quantity": 80}
        )

        # Try to reserve 25 more — only 20 available, should fail
        response = await async_client.post(
            f"/api/v1/inventory/{product_id}/reserve", json={"quantity": 25}
        )
        assert response.status_code == 400
        assert "Available: 20" in response.json()["detail"]

        # Reserve exactly 20 — should succeed
        response = await async_client.post(
            f"/api/v1/inventory/{product_id}/reserve", json={"quantity": 20}
        )
        assert response.status_code == 200
        assert response.json()["reserved"] == 100
