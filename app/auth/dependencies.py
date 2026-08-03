from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidToken
from app.auth.jwt import decode_access_token
from app.db.database import get_db
from app.db.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService
from app.dependencies import UserServiceDep

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    user_service: UserServiceDep,
) -> User:
    payload = decode_access_token(token)

    user_id = payload.get("sub")

    if user_id is None:
        raise InvalidToken()

    return await user_service.get_user(int(user_id))


CurrentUser = Annotated[User, Depends(get_current_user)]
