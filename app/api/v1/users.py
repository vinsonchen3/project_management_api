from fastapi import APIRouter, status

from app.auth.dependencies import CurrentUser
from app.dependencies import AuthServiceDep, UserServiceDep
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.get(
    "/me",
    response_model=UserResponse,
)
async def get_me(
    current_user: CurrentUser,
):
    return current_user


@router.patch(
    "/me",
    response_model=UserResponse,
)
async def update_me(
    user_update: UserUpdate,
    current_user: CurrentUser,
    user_service: UserServiceDep,
):
    return await user_service.update_user(
        current_user=current_user,
        username=user_update.username,
        email=user_update.email,
    )
