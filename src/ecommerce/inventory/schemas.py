"""Inventory request/response schemas."""

from datetime import datetime

from pydantic import BaseModel


class InventoryRead(BaseModel):
    """Schema for inventory responses."""

    product_id: int
    quantity: int
    reserved: int
    last_updated: datetime


class InventoryUpdate(BaseModel):
    """Schema for updating inventory quantity."""

    quantity: int


class ReserveRequest(BaseModel):
    """Schema for reserving inventory."""

    quantity: int
