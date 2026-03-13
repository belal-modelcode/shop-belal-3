"""User business logic service layer."""

from fastapi import HTTPException
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from ecommerce.models import User


async def create_user(session: AsyncSession, email: str, name: str) -> User:
    """Create a new user after checking email uniqueness."""
    result = await session.execute(select(User).where(User.email == email))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=email, name=name)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def get_user(session: AsyncSession, user_id: int) -> User:
    """Get a user by ID or raise 404."""
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def list_users(session: AsyncSession) -> list[User]:
    """List all users."""
    result = await session.execute(select(User))
    return list(result.scalars().all())
