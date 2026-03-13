"""User API endpoints — route definitions only."""

from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from ecommerce.database import get_session
from ecommerce.users.schemas import UserCreate, UserRead
from ecommerce.users import service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate, session: AsyncSession = Depends(get_session)
) -> UserRead:
    """Create a new user."""
    user = await service.create_user(session, data)
    return UserRead.model_validate(user)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int, session: AsyncSession = Depends(get_session)
) -> UserRead:
    """Get user by ID."""
    user = await service.get_user(session, user_id)
    return UserRead.model_validate(user)


@router.get("", response_model=list[UserRead])
async def list_users(session: AsyncSession = Depends(get_session)) -> list[UserRead]:
    """List all users."""
    users = await service.list_users(session)
    return [UserRead.model_validate(u) for u in users]
