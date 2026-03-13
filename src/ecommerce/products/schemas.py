"""Product and category request/response schemas."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    """Schema for creating a new category."""

    name: str
    description: Optional[str] = None


class CategoryRead(BaseModel):
    """Schema for category responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None


class ProductCreate(BaseModel):
    """Schema for creating a new product."""

    name: str
    description: Optional[str] = None
    price: Decimal
    category_id: Optional[int] = None


class ProductRead(BaseModel):
    """Schema for product responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: Optional[str] = None
    price: Decimal
    category_id: Optional[int] = None
    created_at: datetime
