"""Tests for orders API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.fixture
async def seeded_data(async_client: AsyncClient) -> dict:
    """Seed the database with a user, category, products, and inventory for order tests."""
    # Create user
    user_resp = await async_client.post(
        "/api/v1/users", json={"email": "testuser@example.com", "name": "Test User"}
    )
    assert user_resp.status_code == 201
    user_id = user_resp.json()["id"]

    # Create category
    cat_resp = await async_client.post(
        "/api/v1/categories", json={"name": "Electronics"}
    )
    assert cat_resp.status_code == 201
    category_id = cat_resp.json()["id"]

    # Create products
    prod1_resp = await async_client.post(
        "/api/v1/products",
        json={
            "name": "Laptop",
            "price": 999.99,
            "category_id": category_id,
        },
    )
    assert prod1_resp.status_code == 201
    product1_id = prod1_resp.json()["id"]

    prod2_resp = await async_client.post(
        "/api/v1/products",
        json={
            "name": "Mouse",
            "price": 29.99,
            "category_id": category_id,
        },
    )
    assert prod2_resp.status_code == 201
    product2_id = prod2_resp.json()["id"]

    # Set inventory
    await async_client.put(
        f"/api/v1/inventory/{product1_id}", json={"quantity": 50}
    )
    await async_client.put(
        f"/api/v1/inventory/{product2_id}", json={"quantity": 200}
    )

    return {
        "user_id": user_id,
        "product1_id": product1_id,
        "product2_id": product2_id,
    }


class TestCreateOrder:
    """Tests for POST /api/v1/orders."""

    async def test_create_order_success(
        self, async_client: AsyncClient, seeded_data: dict
    ):
        response = await async_client.post(
            "/api/v1/orders",
            json={
                "user_id": seeded_data["user_id"],
                "items": [
                    {"product_id": seeded_data["product1_id"], "quantity": 2},
                    {"product_id": seeded_data["product2_id"], "quantity": 3},
                ],
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == seeded_data["user_id"]
        assert data["user_name"] == "Test User"
        assert data["status"] == "pending"
        # total = 999.99 * 2 + 29.99 * 3 = 1999.98 + 89.97 = 2089.95
        assert float(data["total"]) == pytest.approx(2089.95, abs=0.01)
        assert len(data["items"]) == 2
        assert "id" in data
        assert "created_at" in data

    async def test_create_order_returns_201(
        self, async_client: AsyncClient, seeded_data: dict
    ):
        response = await async_client.post(
            "/api/v1/orders",
            json={
                "user_id": seeded_data["user_id"],
                "items": [
                    {"product_id": seeded_data["product1_id"], "quantity": 1},
                ],
            },
        )
        assert response.status_code == 201

    async def test_create_order_reserves_inventory(
        self, async_client: AsyncClient, seeded_data: dict
    ):
        """Verify that creating an order reserves the correct inventory."""
        await async_client.post(
            "/api/v1/orders",
            json={
                "user_id": seeded_data["user_id"],
                "items": [
                    {"product_id": seeded_data["product1_id"], "quantity": 5},
                ],
            },
        )

        # Check inventory was reserved
        inv_resp = await async_client.get(
            f"/api/v1/inventory/{seeded_data['product1_id']}"
        )
        assert inv_resp.status_code == 200
        inv_data = inv_resp.json()
        assert inv_data["quantity"] == 50
        assert inv_data["reserved"] == 5

    async def test_create_order_user_not_found(
        self, async_client: AsyncClient, seeded_data: dict
    ):
        response = await async_client.post(
            "/api/v1/orders",
            json={
                "user_id": 9999,
                "items": [
                    {"product_id": seeded_data["product1_id"], "quantity": 1},
                ],
            },
        )
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

    async def test_create_order_product_not_found(
        self, async_client: AsyncClient, seeded_data: dict
    ):
        response = await async_client.post(
            "/api/v1/orders",
            json={
                "user_id": seeded_data["user_id"],
                "items": [
                    {"product_id": 9999, "quantity": 1},
                ],
            },
        )
        assert response.status_code == 404
        assert "Product 9999 not found" in response.json()["detail"]

    async def test_create_order_insufficient_inventory(
        self, async_client: AsyncClient, seeded_data: dict
    ):
        response = await async_client.post(
            "/api/v1/orders",
            json={
                "user_id": seeded_data["user_id"],
                "items": [
                    {"product_id": seeded_data["product1_id"], "quantity": 999},
                ],
            },
        )
        assert response.status_code == 400
        assert "Insufficient inventory" in response.json()["detail"]

    async def test_create_order_items_response_format(
        self, async_client: AsyncClient, seeded_data: dict
    ):
        response = await async_client.post(
            "/api/v1/orders",
            json={
                "user_id": seeded_data["user_id"],
                "items": [
                    {"product_id": seeded_data["product1_id"], "quantity": 1},
                ],
            },
        )
        assert response.status_code == 201
        items = response.json()["items"]
        assert len(items) == 1
        item = items[0]
        assert "product_id" in item
        assert "product_name" in item
        assert "quantity" in item
        assert "price" in item
        assert item["product_name"] == "Laptop"
        assert item["quantity"] == 1


class TestGetOrder:
    """Tests for GET /api/v1/orders/{order_id}."""

    async def test_get_order_success(
        self, async_client: AsyncClient, seeded_data: dict
    ):
        # Create an order first
        create_resp = await async_client.post(
            "/api/v1/orders",
            json={
                "user_id": seeded_data["user_id"],
                "items": [
                    {"product_id": seeded_data["product1_id"], "quantity": 1},
                ],
            },
        )
        order_id = create_resp.json()["id"]

        # Get the order
        response = await async_client.get(f"/api/v1/orders/{order_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == order_id
        assert data["user_name"] == "Test User"
        assert len(data["items"]) == 1

    async def test_get_order_not_found(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/orders/9999")
        assert response.status_code == 404
        assert "Order not found" in response.json()["detail"]


class TestListOrders:
    """Tests for GET /api/v1/orders."""

    async def test_list_orders_empty(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/orders")
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_orders_with_data(
        self, async_client: AsyncClient, seeded_data: dict
    ):
        # Create two orders
        for _ in range(2):
            await async_client.post(
                "/api/v1/orders",
                json={
                    "user_id": seeded_data["user_id"],
                    "items": [
                        {"product_id": seeded_data["product2_id"], "quantity": 1},
                    ],
                },
            )

        response = await async_client.get("/api/v1/orders")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

        # List endpoint returns OrderRead (summary without items)
        for order in data:
            assert "id" in order
            assert "user_id" in order
            assert "status" in order
            assert "total" in order
            assert "created_at" in order


class TestCrossDomainOrderFlow:
    """Integration tests for the full order creation flow across domains."""

    async def test_full_order_flow(
        self, async_client: AsyncClient, seeded_data: dict
    ):
        """Test creating an order, checking inventory is reserved, then listing orders."""
        # Create order
        create_resp = await async_client.post(
            "/api/v1/orders",
            json={
                "user_id": seeded_data["user_id"],
                "items": [
                    {"product_id": seeded_data["product1_id"], "quantity": 10},
                    {"product_id": seeded_data["product2_id"], "quantity": 5},
                ],
            },
        )
        assert create_resp.status_code == 201
        order_id = create_resp.json()["id"]

        # Verify inventory reservations
        inv1 = await async_client.get(
            f"/api/v1/inventory/{seeded_data['product1_id']}"
        )
        assert inv1.json()["reserved"] == 10

        inv2 = await async_client.get(
            f"/api/v1/inventory/{seeded_data['product2_id']}"
        )
        assert inv2.json()["reserved"] == 5

        # Get the order and verify details
        get_resp = await async_client.get(f"/api/v1/orders/{order_id}")
        assert get_resp.status_code == 200
        assert len(get_resp.json()["items"]) == 2

        # List orders
        list_resp = await async_client.get("/api/v1/orders")
        assert len(list_resp.json()) == 1

    async def test_multiple_orders_deplete_inventory(
        self, async_client: AsyncClient, seeded_data: dict
    ):
        """Test that multiple orders correctly accumulate reserved inventory."""
        product_id = seeded_data["product2_id"]  # 200 units

        # Order 1: reserve 80
        resp1 = await async_client.post(
            "/api/v1/orders",
            json={
                "user_id": seeded_data["user_id"],
                "items": [{"product_id": product_id, "quantity": 80}],
            },
        )
        assert resp1.status_code == 201

        # Order 2: reserve 100
        resp2 = await async_client.post(
            "/api/v1/orders",
            json={
                "user_id": seeded_data["user_id"],
                "items": [{"product_id": product_id, "quantity": 100}],
            },
        )
        assert resp2.status_code == 201

        # Order 3: try to reserve 25 — only 20 available, should fail
        resp3 = await async_client.post(
            "/api/v1/orders",
            json={
                "user_id": seeded_data["user_id"],
                "items": [{"product_id": product_id, "quantity": 25}],
            },
        )
        assert resp3.status_code == 400
        assert "Insufficient inventory" in resp3.json()["detail"]
