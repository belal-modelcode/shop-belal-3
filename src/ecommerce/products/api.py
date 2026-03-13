"""Product catalog API endpoints — route definitions only."""

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from ecommerce.database import get_session
from ecommerce.products.schemas import (
    CategoryCreate,
    CategoryRead,
    ProductCreate,
    ProductRead,
)
from ecommerce.products import service

router = APIRouter(prefix="/products", tags=["products"])
categories_router = APIRouter(prefix="/categories", tags=["categories"])


@categories_router.post(
    "", response_model=CategoryRead, status_code=status.HTTP_201_CREATED
)
async def create_category(
    data: CategoryCreate, session: AsyncSession = Depends(get_session)
) -> CategoryRead:
    """Create a new category."""
    category = await service.create_category(session, data)
    return CategoryRead.model_validate(category)


@categories_router.get("", response_model=list[CategoryRead])
async def list_categories(
    session: AsyncSession = Depends(get_session),
) -> list[CategoryRead]:
    """List all categories."""
    categories = await service.list_categories(session)
    return [CategoryRead.model_validate(c) for c in categories]


@router.post("", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate, session: AsyncSession = Depends(get_session)
) -> ProductRead:
    """Create a new product."""
    product = await service.create_product(session, data)
    return ProductRead.model_validate(product)


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(
    product_id: int, session: AsyncSession = Depends(get_session)
) -> ProductRead:
    """Get product by ID."""
    product = await service.get_product(session, product_id)
    return ProductRead.model_validate(product)


@router.get("", response_model=list[ProductRead])
async def list_products(
    session: AsyncSession = Depends(get_session),
) -> list[ProductRead]:
    """List all products."""
    products = await service.list_products(session)
    return [ProductRead.model_validate(p) for p in products]
