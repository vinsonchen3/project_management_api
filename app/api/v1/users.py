from fastapi import APIRouter, status

from app.auth.dependencies import CurrentUser
from app.dependencies import AuthServiceDep, UserServiceDep
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.auth import ChangePasswordRequest

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


@router.patch(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def change_password(
    password_update: ChangePasswordRequest,
    current_user: CurrentUser,
    auth_service: AuthServiceDep,
):
    await auth_service.change_password(
        current_user=current_user,
        current_password=password_update.current_password,
        new_password=password_update.new_password,
    )
