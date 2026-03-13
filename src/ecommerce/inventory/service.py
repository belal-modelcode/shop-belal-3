"""Inventory business logic service layer.

Note: The current implementation does not use row-level locking for inventory
operations. This is acceptable for SQLite (which serializes writes) but would
need SELECT ... FOR UPDATE or equivalent locking for PostgreSQL or other
multi-writer databases.
"""

from datetime import datetime

from fastapi import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from ecommerce.models import Inventory


async def get_inventory(session: AsyncSession, product_id: int) -> Inventory:
    """Get inventory for a product or raise 404."""
    inventory = await session.get(Inventory, product_id)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory


async def update_inventory(
    session: AsyncSession, product_id: int, quantity: int
) -> Inventory:
    """Update the total quantity of inventory for a product."""
    inventory = await session.get(Inventory, product_id)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")

    inventory.quantity = quantity
    inventory.last_updated = datetime.utcnow()
    session.add(inventory)
    await session.commit()
    await session.refresh(inventory)
    return inventory


async def reserve_inventory(
    session: AsyncSession, product_id: int, quantity: int
) -> Inventory:
    """Reserve inventory for an order.

    Checks that sufficient unreserved stock exists before reserving.
    """
    inventory = await session.get(Inventory, product_id)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")

    available = inventory.quantity - inventory.reserved
    if available < quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient inventory. Available: {available}, Requested: {quantity}",
        )

    inventory.reserved += quantity
    inventory.last_updated = datetime.utcnow()
    session.add(inventory)
    await session.commit()
    await session.refresh(inventory)
    return inventory
