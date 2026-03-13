"""User request/response schemas."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    email: str
    name: str


class UserRead(BaseModel):
    """Schema for user responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    created_at: datetime
