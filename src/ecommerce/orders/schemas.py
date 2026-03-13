"""Order request/response schemas."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class OrderItemRequest(BaseModel):
    """Schema for an item in a create-order request."""

    product_id: int
    quantity: int


class CreateOrderRequest(BaseModel):
    """Schema for creating a new order."""

    user_id: int
    items: list[OrderItemRequest]


class OrderItemResponse(BaseModel):
    """Schema for an order item in responses."""

    product_id: int
    product_name: str
    quantity: int
    price: float


class OrderResponse(BaseModel):
    """Detailed order response with user name and items."""

    id: int
    user_id: int
    user_name: str
    status: str
    total: Decimal
    created_at: datetime
    items: list[OrderItemResponse]


class OrderRead(BaseModel):
    """Summary order response for list endpoints."""

    id: int
    user_id: int
    status: str
    total: Decimal
    created_at: datetime
