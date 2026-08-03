from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserResponse
from app.dependencies import AuthServiceDep

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    user_data: UserCreate,
    auth_service: AuthServiceDep,
):
    return await auth_service.register(
        username=user_data.username, email=user_data.email, password=user_data.password
    )


@router.post(
    "/login",
    response_model=TokenResponse,
)
async def login(
    user_credentials: LoginRequest,
    auth_service: AuthServiceDep,
):
    token = await auth_service.login(
        email=user_credentials.email, password=user_credentials.password
    )
    return TokenResponse(access_token=token)


@router.post(
    "/token",
    response_model=TokenResponse,
)
async def login_for_swagger(
    auth_service: AuthServiceDep,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    token = await auth_service.login(
        email=form_data.username,
        password=form_data.password,
    )
    return TokenResponse(access_token=token)
