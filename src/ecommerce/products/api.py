"""Product catalog API endpoints."""

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from ecommerce.database import get_session
from ecommerce.products.schemas import (
    CategoryCreate,
    CategoryRead,
    ProductCreate,
    ProductRead,
)
from ecommerce.products.service import (
    create_category,
    create_product,
    get_product,
    list_categories,
    list_products,
)

router = APIRouter(prefix="/products", tags=["products"])
categories_router = APIRouter(prefix="/categories", tags=["categories"])


@categories_router.post("", response_model=CategoryRead, status_code=201)
async def create_category_endpoint(
    data: CategoryCreate, session: AsyncSession = Depends(get_session)
) -> CategoryRead:
    """Create a new category."""
    cat = await create_category(session, name=data.name, description=data.description)
    return CategoryRead(id=cat.id, name=cat.name, description=cat.description)


@categories_router.get("", response_model=list[CategoryRead])
async def list_categories_endpoint(
    session: AsyncSession = Depends(get_session),
) -> list[CategoryRead]:
    """List all categories."""
    cats = await list_categories(session)
    return [CategoryRead(id=c.id, name=c.name, description=c.description) for c in cats]


@router.post("", response_model=ProductRead, status_code=201)
async def create_product_endpoint(
    data: ProductCreate, session: AsyncSession = Depends(get_session)
) -> ProductRead:
    """Create a new product."""
    product = await create_product(
        session,
        name=data.name,
        price=data.price,
        description=data.description,
        category_id=data.category_id,
    )
    return ProductRead(
        id=product.id,
        name=product.name,
        description=product.description,
        price=product.price,
        category_id=product.category_id,
        created_at=product.created_at,
    )


@router.get("/{product_id}", response_model=ProductRead)
async def get_product_endpoint(
    product_id: int, session: AsyncSession = Depends(get_session)
) -> ProductRead:
    """Get product by ID."""
    product = await get_product(session, product_id)
    return ProductRead(
        id=product.id,
        name=product.name,
        description=product.description,
        price=product.price,
        category_id=product.category_id,
        created_at=product.created_at,
    )


@router.get("", response_model=list[ProductRead])
async def list_products_endpoint(
    session: AsyncSession = Depends(get_session),
) -> list[ProductRead]:
    """List all products."""
    products = await list_products(session)
    return [
        ProductRead(
            id=p.id,
            name=p.name,
            description=p.description,
            price=p.price,
            category_id=p.category_id,
            created_at=p.created_at,
        )
        for p in products
    ]
