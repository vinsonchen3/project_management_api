from app.core.exceptions import (
    ProjectNotFoundError,
    UserNotFoundError,
    PermissionDeniedError,
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
        current_user: User,
        name: str,
        description: str | None,
    ) -> Project:
        return await self.project_repo.create(
            name=name,
            description=description,
            owner=current_user,
        )

    async def get_project(
        self,
        current_user: User,
        project_id: int,
    ) -> Project:
        project = await self.project_repo.get_by_id_detailed(project_id)

        if project is None:
            raise ProjectNotFoundError()

        await self._require_project_member(project, current_user)

        return project

    async def get_projects(
        self,
        current_user: User,
    ) -> list[Project]:
        return await self.project_repo.get_for_user(current_user.id)

    async def delete_project(
        self,
        current_user: User,
        project_id: int,
    ) -> None:
        project = await self.project_repo.get_by_id(project_id)

        if project is None:
            raise ProjectNotFoundError()

        await self._require_project_owner(project, current_user)

        await self.project_repo.delete(project)

    async def update_project(
        self,
        current_user: User,
        project_id: int,
        name: str | None,
        description: str | None,
    ) -> Project:
        project = await self.project_repo.get_by_id(project_id)

        if project is None:
            raise ProjectNotFoundError()

        await self._require_project_owner(project, current_user)

        if name is not None:
            project.name = name

        if description is not None:
            project.description = description

        return await self.project_repo.update(project)

    async def add_member(
        self,
        current_user: User,
        project_id: int,
        user_id: int,
    ) -> Project:
        project = await self.project_repo.get_by_id_with_members(project_id)
        if project is None:
            raise ProjectNotFoundError()

        await self._require_project_owner(project, current_user)

        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError()

        if user not in project.members:
            project.members.append(user)

        return await self.project_repo.update(project)

    async def remove_member(
        self,
        current_user: User,
        project_id: int,
        user_id: int,
    ) -> Project:
        project = await self.project_repo.get_by_id_with_members(project_id)
        if project is None:
            raise ProjectNotFoundError()

        await self._require_project_owner(project, current_user)

        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError()

        if user in project.members:
            project.members.remove(user)

        return await self.project_repo.update(project)

    async def leave_project(
        self,
        current_user: User,
        project_id: int,
    ) -> None:
        project = await self.project_repo.get_by_id_with_members(project_id)
        if project is None:
            raise ProjectNotFoundError()

        if project.owner_id == current_user.id:
            raise PermissionDeniedError("Project owner cannot leave project")

        if current_user in project.members:
            project.members.remove(current_user)
        await self.project_repo.update(project)

    async def get_members(
        self,
        current_user: User,
        project_id: int,
    ) -> list[User]:
        project = await self.project_repo.get_by_id_with_members(project_id)
        if project is None:
            raise ProjectNotFoundError()

        await self._require_project_member(project, current_user)

        return project.members

    async def get_tasks(
        self,
        current_user: User,
        project_id: int,
    ) -> list[Task]:
        project = await self.project_repo.get_by_id_detailed(project_id)
        if project is None:
            raise ProjectNotFoundError()

        await self._require_project_member(project, current_user)

        return project.tasks

    async def _require_project_member(
        self,
        project: Project,
        current_user: User,
    ) -> None:
        if current_user not in project.members:
            raise PermissionDeniedError()

    async def _require_project_owner(
        self,
        project: Project,
        current_user: User,
    ) -> None:
        if project.owner_id != current_user.id:
            raise PermissionDeniedError()
