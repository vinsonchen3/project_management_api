from app.repositories.user_repository import UserRepository
from app.core.exceptions import (
    UserNotFoundError,
    DuplicateEmailError,
    DuplicateUsernameError,
)
from db.models.user import User


class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def create_user(
        self,
        username: str,
        email: str,
        password: str,
    ) -> User:
        if await self.user_repo.exists_by_username(username):
            raise DuplicateUsernameError

        if await self.user_repo.exists_by_email(email):
            raise DuplicateEmailError

        return await self.user_repo.create(
            username=username,
            email=email,
            hashed_password=password,  # TODO: fix this method with hash(password) when i add auth
        )

    async def get_user(self, user_id: int) -> User:
        user = await self.user_repo.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError()

        return user

    async def get_users(
        self,
        offset: int = 0,
        limit: int = 100,
    ) -> list[User]:
        return await self.user_repo.get_all(
            offset=offset,
            limit=limit,
        )

    async def update_user(
        self,
        user_id: int,
        username: str | None = None,
        email: str | None = None,
        password: str | None = None,
    ) -> User:
        user = await self.user_repo.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError()

        if username is not None:
            existing = await self.user_repo.get_by_username(username)
            if existing is not None and existing.id != user.id:
                raise DuplicateUsernameError()
            user.username = username

        if email is not None:
            existing = await self.user_repo.get_by_email(email)
            if existing is not None and existing.id != user.id:
                raise DuplicateEmailError()
            user.email = email

        if password is not None:
            # TODO: Replace with hash_password(password)
            user.hashed_password = password

        return await self.user_repo.update(user)

    async def delete_user(self, user_id: int) -> None:
        user = await self.user_repo.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError()

        await self.user_repo.delete(user)