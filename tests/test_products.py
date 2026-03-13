"""Tests for product and category API endpoints."""

import pytest
from httpx import AsyncClient


class TestCreateCategory:
    """Tests for POST /api/v1/categories."""

    async def test_create_category_success(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/categories",
            json={"name": "Electronics", "description": "Electronic devices"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Electronics"
        assert data["description"] == "Electronic devices"
        assert "id" in data

    async def test_create_category_no_description(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/categories",
            json={"name": "Books"},
        )
        assert response.status_code == 201
        assert response.json()["description"] is None

    async def test_create_category_missing_name(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/categories",
            json={"description": "No name provided"},
        )
        assert response.status_code == 422


class TestListCategories:
    """Tests for GET /api/v1/categories."""

    async def test_list_categories_empty(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/categories")
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_categories_with_data(self, async_client: AsyncClient):
        await async_client.post(
            "/api/v1/categories", json={"name": "Cat1"}
        )
        await async_client.post(
            "/api/v1/categories", json={"name": "Cat2"}
        )
        response = await async_client.get("/api/v1/categories")
        assert response.status_code == 200
        assert len(response.json()) == 2


class TestCreateProduct:
    """Tests for POST /api/v1/products."""

    async def test_create_product_success(self, async_client: AsyncClient):
        # Create a category first
        cat_resp = await async_client.post(
            "/api/v1/categories", json={"name": "Gadgets"}
        )
        cat_id = cat_resp.json()["id"]

        response = await async_client.post(
            "/api/v1/products",
            json={
                "name": "Widget",
                "description": "A useful widget",
                "price": 19.99,
                "category_id": cat_id,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Widget"
        assert float(data["price"]) == 19.99
        assert data["category_id"] == cat_id
        assert "id" in data
        assert "created_at" in data

    async def test_create_product_no_category(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/products",
            json={"name": "Standalone", "price": 5.00},
        )
        assert response.status_code == 201
        assert response.json()["category_id"] is None

    async def test_create_product_invalid_category(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/products",
            json={"name": "Bad Cat", "price": 10.00, "category_id": 9999},
        )
        assert response.status_code == 404
        assert "Category not found" in response.json()["detail"]

    async def test_create_product_missing_price(self, async_client: AsyncClient):
        response = await async_client.post(
            "/api/v1/products",
            json={"name": "No Price"},
        )
        assert response.status_code == 422

    async def test_create_product_initializes_inventory(
        self, async_client: AsyncClient
    ):
        """Product creation should also create an inventory record."""
        resp = await async_client.post(
            "/api/v1/products",
            json={"name": "Inventoried", "price": 15.00},
        )
        product_id = resp.json()["id"]

        # Check inventory via the existing inventory endpoint
        inv_resp = await async_client.get(f"/api/v1/inventory/{product_id}")
        assert inv_resp.status_code == 200
        inv_data = inv_resp.json()
        assert inv_data["quantity"] == 0
        assert inv_data["reserved"] == 0


class TestGetProduct:
    """Tests for GET /api/v1/products/{product_id}."""

    async def test_get_product_success(self, async_client: AsyncClient):
        create_resp = await async_client.post(
            "/api/v1/products",
            json={"name": "Fetchable", "price": 25.00},
        )
        product_id = create_resp.json()["id"]

        response = await async_client.get(f"/api/v1/products/{product_id}")
        assert response.status_code == 200
        assert response.json()["name"] == "Fetchable"

    async def test_get_product_not_found(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/products/9999")
        assert response.status_code == 404
        assert "Product not found" in response.json()["detail"]


class TestListProducts:
    """Tests for GET /api/v1/products."""

    async def test_list_products_empty(self, async_client: AsyncClient):
        response = await async_client.get("/api/v1/products")
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_products_with_data(self, async_client: AsyncClient):
        await async_client.post(
            "/api/v1/products", json={"name": "P1", "price": 1.00}
        )
        await async_client.post(
            "/api/v1/products", json={"name": "P2", "price": 2.00}
        )
        response = await async_client.get("/api/v1/products")
        assert response.status_code == 200
        assert len(response.json()) == 2
