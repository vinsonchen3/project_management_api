from fastapi import APIRouter, status

from app.auth.dependencies import CurrentUser
from app.dependencies import ProjectServiceDep
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse,
    ProjectDetailed,
)
from app.schemas.user import UserResponse
from app.schemas.task import TaskResponse

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