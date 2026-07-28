from app.repositories.user_repository import UserRepository
from app.core.exceptions import (
    UserNotFoundError,
    DuplicateEmailError,
    DuplicateUsernameError,
)
from app.db.models.user import User
from app.auth.hashing import hash_password


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
            raise DuplicateUsernameError()

        if await self.user_repo.exists_by_email(email):
            raise DuplicateEmailError()

        return await self.user_repo.create(
            username=username,
            email=email,
            hashed_password=hash_password(password),
        )

    async def get_user(self, user_id: int) -> User:
        user = await self.user_repo.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError()

        return user

    async def get_user_by_email(self, email: str) -> User | None:
        return await self.user_repo.get_by_email(email)

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
        current_user: User,
        username: str | None = None,
        email: str | None = None,
        password: str | None = None,
    ) -> User:
        if username is not None:
            existing = await self.user_repo.get_by_username(username)
            if existing is not None and existing.id != current_user.id:
                raise DuplicateUsernameError()
            current_user.username = username

        if email is not None:
            existing = await self.user_repo.get_by_email(email)
            if existing is not None and existing.id != current_user.id:
                raise DuplicateEmailError()
            current_user.email = email

        if password is not None:
            current_user.hashed_password = hash_password(password)

        return await self.user_repo.update(current_user)

    async def update_password(
        self,
        current_user: User,
        password: str,
    ) -> User:
        current_user.hashed_password = hash_password(password)
        return await self.user_repo.update(current_user)

    async def delete_user(
        self,
        current_user: User,
    ) -> None:
        await self.user_repo.delete(current_user)