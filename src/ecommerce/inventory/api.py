"""Inventory management API endpoints."""

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from ecommerce.database import get_session
from ecommerce.inventory.schemas import InventoryRead, InventoryUpdate, ReserveRequest
from ecommerce.inventory.service import (
    get_inventory,
    reserve_inventory,
    update_inventory,
)

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/{product_id}", response_model=InventoryRead)
async def get_inventory_endpoint(
    product_id: int, session: AsyncSession = Depends(get_session)
) -> InventoryRead:
    """Get inventory for a product."""
    inv = await get_inventory(session, product_id)
    return InventoryRead(
        product_id=inv.product_id,
        quantity=inv.quantity,
        reserved=inv.reserved,
        last_updated=inv.last_updated,
    )


@router.put("/{product_id}", response_model=InventoryRead)
async def update_inventory_endpoint(
    product_id: int,
    data: InventoryUpdate,
    session: AsyncSession = Depends(get_session),
) -> InventoryRead:
    """Update inventory quantity."""
    inv = await update_inventory(session, product_id, quantity=data.quantity)
    return InventoryRead(
        product_id=inv.product_id,
        quantity=inv.quantity,
        reserved=inv.reserved,
        last_updated=inv.last_updated,
    )


@router.post("/{product_id}/reserve", response_model=InventoryRead)
async def reserve_inventory_endpoint(
    product_id: int,
    data: ReserveRequest,
    session: AsyncSession = Depends(get_session),
) -> InventoryRead:
    """Reserve inventory for an order."""
    inv = await reserve_inventory(session, product_id, quantity=data.quantity)
    return InventoryRead(
        product_id=inv.product_id,
        quantity=inv.quantity,
        reserved=inv.reserved,
        last_updated=inv.last_updated,
    )
