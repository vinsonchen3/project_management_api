from app.core.exceptions import InvalidCredentials, InvalidToken
from app.auth.hashing import hash_password, verify_password
from app.auth.jwt import create_access_token, decode_access_token
from app.core.exceptions import UserNotFoundError
from app.services.user_service import UserService


class AuthService:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    async def register(
        self,
        username: str,
        email: str,
        password: str,
    ):
        return await self.user_service.create_user(
            username=username,
            email=email,
            password=password,
        )

    async def login(
        self,
        email: str,
        password: str,
    ) -> str:
        user = await self.user_service.get_user_by_email(email)

        if user is None:
            raise InvalidCredentials()

        if not verify_password(
            password,
            user.hashed_password,
        ):
            raise InvalidCredentials()

        return create_access_token(
            {
                "sub": str(user.id),
            }
        )

    async def refresh(
        self,
        token: str,
    ) -> str:
        payload = decode_access_token(token)

        user_id = payload.get("sub")

        if user_id is None:
            raise InvalidToken()

        user = await self.user_service.get_user(int(user_id))

        return create_access_token(
            {
                "sub": str(user.id),
            }
        )

    async def change_password(
        self,
        user_id: int,
        current_password: str,
        new_password: str,
    ):
        user = await self.user_service.get_user(user_id)

        if not verify_password(
            current_password,
            user.hashed_password,
        ):
            raise InvalidCredentials()

        user.hashed_password = hash_password(new_password)

        return await self.user_service.user_repo.update(user)