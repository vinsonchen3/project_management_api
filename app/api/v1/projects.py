from fastapi import APIRouter, status

from app.auth.dependencies import CurrentUser
from app.dependencies import ProjectServiceDep, TaskServiceDep
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectDetailed,
)
from app.schemas.user import UserResponse
from app.schemas.task import TaskResponse, TaskCreate

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post(
    "/",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_project(
    project: ProjectCreate,
    current_user: CurrentUser,
    project_service: ProjectServiceDep,
):
    return await project_service.create_project(
        current_user=current_user,
        name=project.name,
        description=project.description,
    )


@router.get(
    "/",
    response_model=list[ProjectResponse],
)
async def get_projects(
    current_user: CurrentUser,
    project_service: ProjectServiceDep,
):
    return await project_service.get_projects(current_user)


@router.get(
    "/{project_id}",
    response_model=ProjectDetailed,
)
async def get_project(
    project_id: int,
    current_user: CurrentUser,
    project_service: ProjectServiceDep,
):
    return await project_service.get_project(
        current_user=current_user,
        project_id=project_id,
    )


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
)
async def update_project(
    project_id: int,
    project: ProjectUpdate,
    current_user: CurrentUser,
    project_service: ProjectServiceDep,
):
    return await project_service.update_project(
        current_user=current_user,
        project_id=project_id,
        name=project.name,
        description=project.description,
    )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_project(
    project_id: int,
    current_user: CurrentUser,
    project_service: ProjectServiceDep,
):
    await project_service.delete_project(
        current_user=current_user,
        project_id=project_id,
    )


@router.get(
    "/{project_id}/members",
    response_model=list[UserResponse],
)
async def get_members(
    project_id: int,
    current_user: CurrentUser,
    project_service: ProjectServiceDep,
):
    return await project_service.get_members(
        current_user=current_user,
        project_id=project_id,
    )


@router.post(
    "/{project_id}/members",
    response_model=ProjectResponse,
)
async def add_member(  # for add_member because i have request as a query parameter i need to send it in the frontend
    project_id: int,
    user_id: int,
    current_user: CurrentUser,
    project_service: ProjectServiceDep,
):
    return await project_service.add_member(
        current_user=current_user,
        project_id=project_id,
        user_id=user_id,
    )


@router.delete(
    "/{project_id}/members/{user_id}",
    response_model=ProjectResponse,
)
async def remove_member(
    project_id: int,
    user_id: int,
    current_user: CurrentUser,
    project_service: ProjectServiceDep,
):
    return await project_service.remove_member(
        current_user=current_user,
        project_id=project_id,
        user_id=user_id,
    )


@router.delete(
    "/{project_id}/members/me",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def leave_project(
    project_id: int,
    current_user: CurrentUser,
    project_service: ProjectServiceDep,
):
    await project_service.leave_project(
        current_user=current_user,
        project_id=project_id,
    )


@router.post(
    "/{project_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    project_id: int,
    task: TaskCreate,
    current_user: CurrentUser,
    task_service: TaskServiceDep,
):
    return await task_service.create_task(
        current_user=current_user,
        title=task.title,
        description=task.description,
        project_id=project_id,
        status=task.status,
    )


@router.get(
    "/{project_id}/tasks",
    response_model=list[TaskResponse],
)
async def get_tasks(
    project_id: int,
    current_user: CurrentUser,
    project_service: ProjectServiceDep,
):
    return await project_service.get_tasks(
        current_user=current_user,
        project_id=project_id,
    )
