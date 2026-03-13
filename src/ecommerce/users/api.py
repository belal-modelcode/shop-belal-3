"""User API endpoints."""

from fastapi import APIRouter, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from ecommerce.database import get_session
from ecommerce.users.schemas import UserCreate, UserRead
from ecommerce.users.service import create_user, get_user, list_users

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=201)
async def create_user_endpoint(
    data: UserCreate, session: AsyncSession = Depends(get_session)
) -> UserRead:
    """Create a new user."""
    user = await create_user(session, email=data.email, name=data.name)
    return UserRead(
        id=user.id, email=user.email, name=user.name, created_at=user.created_at
    )


@router.get("/{user_id}", response_model=UserRead)
async def get_user_endpoint(
    user_id: int, session: AsyncSession = Depends(get_session)
) -> UserRead:
    """Get user by ID."""
    user = await get_user(session, user_id)
    return UserRead(
        id=user.id, email=user.email, name=user.name, created_at=user.created_at
    )


@router.get("", response_model=list[UserRead])
async def list_users_endpoint(
    session: AsyncSession = Depends(get_session),
) -> list[UserRead]:
    """List all users."""
    users = await list_users(session)
    return [
        UserRead(id=u.id, email=u.email, name=u.name, created_at=u.created_at)
        for u in users
    ]
