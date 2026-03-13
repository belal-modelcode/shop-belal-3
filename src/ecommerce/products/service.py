"""Product and category business logic service layer."""

from decimal import Decimal
from typing import Optional

from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ecommerce.models import Category, Inventory, Product


async def create_category(
    session: AsyncSession, name: str, description: Optional[str] = None
) -> Category:
    """Create a new category."""
    category = Category(name=name, description=description)
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


async def list_categories(session: AsyncSession) -> list[Category]:
    """List all categories."""
    result = await session.execute(select(Category))
    return list(result.scalars().all())


async def create_product(
    session: AsyncSession,
    name: str,
    price: Decimal,
    description: Optional[str] = None,
    category_id: Optional[int] = None,
) -> Product:
    """Create a new product and initialize its inventory."""
    if category_id:
        category = await session.get(Category, category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

    product = Product(
        name=name, description=description, price=price, category_id=category_id
    )
    session.add(product)
    await session.commit()
    await session.refresh(product)

    # Initialize inventory for new product
    inventory = Inventory(product_id=product.id, quantity=0, reserved=0)
    session.add(inventory)
    await session.commit()
    await session.refresh(product)

    return product


async def get_product(session: AsyncSession, product_id: int) -> Product:
    """Get a product by ID or raise 404."""
    product = await session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


async def list_products(session: AsyncSession) -> list[Product]:
    """List all products."""
    result = await session.execute(select(Product))
    return list(result.scalars().all())
