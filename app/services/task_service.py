from app.core.exceptions import (
    TaskNotFoundError,
    ProjectNotFoundError,
    UserNotFoundError,
    PermissionDeniedError,
    UserNotInProjectError,
)

from app.repositories.task_repository import TaskRepository
from app.repositories.project_repository import ProjectRepository
from app.repositories.user_repository import UserRepository

from app.db.enums import TaskStatus
from app.db.models.task import Task
from app.db.models.user import User
from app.db.models.comment import Comment
from app.db.models.project import Project


class TaskService:
    def __init__(
        self,
        task_repo: TaskRepository,
        project_repo: ProjectRepository,
        user_repo: UserRepository,
    ):
        self.task_repo = task_repo
        self.project_repo = project_repo
        self.user_repo = user_repo

    async def create_task(
        self,
        current_user: User,
        title: str,
        description: str | None,
        project_id: int,
        status: TaskStatus = TaskStatus.TO_DO,
    ) -> Task:
        project = await self.project_repo.get_by_id_with_members(project_id)

        if project is None:
            raise ProjectNotFoundError()

        await self._require_project_member(project, current_user)

        return await self.task_repo.create(
            title=title,
            description=description,
            status=status,
            project_id=project_id,
        )

    async def update_task(
        self,
        current_user: User,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
        status: TaskStatus | None = None,
    ) -> Task:
        task = await self.task_repo.get_by_id_with_project_members(task_id)

        if task is None:
            raise TaskNotFoundError()

        await self._require_project_member(task.project, current_user)

        if title is not None:
            task.title = title

        if description is not None:
            task.description = description

        if status is not None:
            task.status = status

        return await self.task_repo.update(task)

    async def delete_task(
        self,
        current_user: User,
        task_id: int,
    ) -> None:
        task = await self.task_repo.get_by_id_with_project_members(task_id)

        if task is None:
            raise TaskNotFoundError()

        await self._require_project_member(task.project, current_user)

        await self.task_repo.delete(task)

    async def assign_user(
        self,
        current_user: User,
        task_id: int,
        user_id: int,
    ) -> Task:
        task = await self.task_repo.get_by_id_with_assignees(task_id)

        if task is None:
            raise TaskNotFoundError()

        await self._require_project_member(task.project, current_user)

        user = await self.user_repo.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError()

        if user not in task.project.members:
            raise UserNotInProjectError()

        if user not in task.assignees:
            task.assignees.append(user)

        return await self.task_repo.update(task)

    async def remove_assignee(
        self,
        current_user: User,
        task_id: int,
        user_id: int,
    ) -> Task:
        task = await self.task_repo.get_by_id_with_assignees(task_id)

        if task is None:
            raise TaskNotFoundError()

        await self._require_project_member(task.project, current_user)

        user = await self.user_repo.get_by_id(user_id)

        if user is None:
            raise UserNotFoundError()

        if user in task.assignees:
            task.assignees.remove(user)

        return await self.task_repo.update(task)

    async def get_comments(
        self,
        current_user: User,
        task_id: int,
    ) -> list[Comment]:
        task = await self.task_repo.get_by_id_detailed(task_id)

        if task is None:
            raise TaskNotFoundError()

        await self._require_project_member(task.project, current_user)

        return task.comments

    async def get_assignees(
        self,
        current_user: User,
        task_id: int,
    ) -> list[User]:
        task = await self.task_repo.get_by_id_with_assignees(task_id)

        if task is None:
            raise TaskNotFoundError()

        await self._require_project_member(task.project, current_user)

        return task.assignees

    async def get_task(
        self,
        current_user: User,
        task_id: int,
    ) -> Task:
        task = await self.task_repo.get_by_id_detailed(task_id)

        if task is None:
            raise TaskNotFoundError()

        await self._require_project_member(task.project, current_user)

        return task

    async def _require_project_member(
        self,
        project: Project,
        current_user: User,
    ) -> None:
        if current_user not in project.members:
            raise PermissionDeniedError()
