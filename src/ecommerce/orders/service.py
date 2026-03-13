"""Order business logic service layer.

This service orchestrates the full order creation transaction including
user validation, product/inventory checks, order+item creation, and
inventory reservation. It uses session.flush() (not commit) to obtain
the order ID before creating items, letting the caller (route handler)
control the final commit.

Cross-module dependencies: This service directly queries User, Product,
and Inventory ORM models since all models are co-located in models.py.
This is pragmatic for a monolith — adding inter-service calls would be
premature abstraction.
"""

from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ecommerce.models import Inventory, Order, OrderItem, Product, User
from ecommerce.orders.schemas import OrderItemResponse, OrderResponse


async def create_order(
    session: AsyncSession, user_id: int, items: list[dict]
) -> OrderResponse:
    """Create an order with items and reserve inventory.

    This function performs the entire order creation flow as a single
    transaction:
    1. Validate the user exists
    2. Validate each product exists and has sufficient inventory
    3. Create the order record (flush to get ID)
    4. Create order items and reserve inventory
    5. Commit the transaction

    Args:
        session: Database session
        user_id: ID of the user placing the order
        items: List of dicts with 'product_id' and 'quantity' keys

    Returns:
        OrderResponse with full order details

    Raises:
        HTTPException 404: If user, product, or inventory not found
        HTTPException 400: If insufficient inventory for any item
    """
    # Verify user exists
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_name = user.name

    # Validate products and calculate total
    total = Decimal(0)
    order_items_data = []

    for item_req in items:
        product_id = item_req["product_id"]
        quantity = item_req["quantity"]

        product = await session.get(Product, product_id)
        if not product:
            raise HTTPException(
                status_code=404, detail=f"Product {product_id} not found"
            )

        # Check inventory availability
        inventory = await session.get(Inventory, product_id)
        if not inventory:
            raise HTTPException(
                status_code=404,
                detail=f"Inventory not found for product {product_id}",
            )

        available = inventory.quantity - inventory.reserved
        if available < quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient inventory for {product.name}. Available: {available}",
            )

        item_total = product.price * quantity
        total += item_total

        order_items_data.append(
            {
                "product": product,
                "quantity": quantity,
                "price": product.price,
                "inventory": inventory,
            }
        )

    # Create order — flush to get the order ID before creating items
    order = Order(user_id=user_id, status="pending", total=total)
    session.add(order)
    await session.flush()

    # Create order items and reserve inventory
    items_response = []
    for item_data in order_items_data:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item_data["product"].id,
            quantity=item_data["quantity"],
            price=item_data["price"],
        )
        session.add(order_item)

        # Reserve inventory
        inventory = item_data["inventory"]
        inventory.reserved += item_data["quantity"]
        inventory.last_updated = datetime.utcnow()
        session.add(inventory)

        items_response.append(
            OrderItemResponse(
                product_id=item_data["product"].id,
                product_name=item_data["product"].name,
                quantity=item_data["quantity"],
                price=float(item_data["price"]),
            )
        )

    await session.commit()
    await session.refresh(order)

    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        user_name=user_name,
        status=order.status,
        total=order.total,
        created_at=order.created_at,
        items=items_response,
    )


async def get_order(session: AsyncSession, order_id: int) -> OrderResponse:
    """Get order details with items and user info."""
    order = await session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    user = await session.get(User, order.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_name = user.name

    result = await session.execute(
        select(OrderItem).where(OrderItem.order_id == order_id)
    )
    order_items = result.scalars().all()

    items_response = []
    for item in order_items:
        product = await session.get(Product, item.product_id)
        if product:
            items_response.append(
                OrderItemResponse(
                    product_id=product.id,
                    product_name=product.name,
                    quantity=item.quantity,
                    price=float(item.price),
                )
            )

    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        user_name=user_name,
        status=order.status,
        total=order.total,
        created_at=order.created_at,
        items=items_response,
    )


async def list_orders(session: AsyncSession) -> list[Order]:
    """List all orders."""
    result = await session.execute(select(Order))
    return list(result.scalars().all())
