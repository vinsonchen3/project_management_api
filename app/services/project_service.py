from app.core.exceptions import (
    ProjectNotFoundError,
    UserNotFoundError,
)

from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository

from app.db.models.project import Project
from app.db.models.user import User
from app.db.models.task import Task


class ProjectService:
    def __init__(
        self,
        project_repo: ProjectRepository,
        user_repo: UserRepository,
    ):
        self.project_repo = project_repo
        self.user_repo = user_repo

    async def create_project(
        self,
        name: str,
        description: str | None,
        owner_id: int,
    ) -> Project:
        owner = await self.user_repo.get_by_id(owner_id)

        if owner is None:
            raise UserNotFoundError()

        return await self.project_repo.create(
            name=name,
            description=description,
            owner_id=owner_id,
        )

    async def get_project(
        self,
        project_id: int,
    ) -> Project:
        project = await self.project_repo.get_by_id_detailed(project_id)
        if project is None:
            raise ProjectNotFoundError()

        return project

    async def delete_project(
        self,
        project_id: int,
    ) -> None:
        project = await self.project_repo.get_by_id(project_id)

        if project is None:
            raise ProjectNotFoundError()

        await self.project_repo.delete(project)

    async def rename_project(
        self,
        project_id: int,
        name: str,
    ) -> Project:
        project = await self.project_repo.get_by_id(project_id)

        if project is None:
            raise ProjectNotFoundError()

        project.name = name

        return await self.project_repo.update(project)

    async def update_description(
        self,
        project_id: int,
        description: str | None,
    ) -> Project:
        project = await self.project_repo.get_by_id(project_id)

        if project is None:
            raise ProjectNotFoundError()

        project.description = description

        return await self.project_repo.update(project)

    async def add_member(
        self,
        project_id: int,
        user_id: int,
    ) -> Project:
        project = await self.project_repo.get_by_id_with_members(project_id)
        if project is None:
            raise ProjectNotFoundError()

        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError()

        if user not in project.members:
            project.members.append(user)

        return await self.project_repo.update(project)

    async def remove_member(
        self,
        project_id: int,
        user_id: int,
    ) -> Project:
        project = await self.project_repo.get_by_id_with_members(project_id)
        if project is None:
            raise ProjectNotFoundError()

        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError()

        if user in project.members:
            project.members.remove(user)

        return await self.project_repo.update(project)

    async def get_members(
        self,
        project_id: int,
    ) -> list[User]:
        project = await self.project_repo.get_by_id_with_members(project_id)
        if project is None:
            raise ProjectNotFoundError()

        return project.members

    async def get_tasks(
        self,
        project_id: int,
    ) -> list[Task]:
        project = await self.project_repo.get_by_id_detailed(project_id)
        if project is None:
            raise ProjectNotFoundError()

        return project.tasks
