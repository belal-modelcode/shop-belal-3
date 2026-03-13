"""Order management API endpoints."""

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from ecommerce.database import get_session
from ecommerce.orders.schemas import CreateOrderRequest, OrderRead, OrderResponse
from ecommerce.orders.service import (
    create_order,
    get_order,
    list_orders,
)

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=201)
async def create_order_endpoint(
    request: CreateOrderRequest, session: AsyncSession = Depends(get_session)
) -> OrderResponse:
    """Create a new order with items and inventory reservation."""
    items = [
        {"product_id": item.product_id, "quantity": item.quantity}
        for item in request.items
    ]
    return await create_order(session, user_id=request.user_id, items=items)


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_endpoint(
    order_id: int, session: AsyncSession = Depends(get_session)
) -> OrderResponse:
    """Get order details with items."""
    return await get_order(session, order_id)


@router.get("", response_model=list[OrderRead])
async def list_orders_endpoint(
    session: AsyncSession = Depends(get_session),
) -> list[OrderRead]:
    """List all orders."""
    orders = await list_orders(session)
    return [
        OrderRead(
            id=o.id,
            user_id=o.user_id,
            status=o.status,
            total=o.total,
            created_at=o.created_at,
        )
        for o in orders
    ]
