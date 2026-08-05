from fastapi import APIRouter, status

from app.auth.dependencies import CurrentUser
from app.dependencies import TaskServiceDep

from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskAssignment,
    TaskResponse,
    TaskDetailed,
)
from app.schemas.comment import CommentResponse

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    task: TaskCreate,
    current_user: CurrentUser,
    task_service: TaskServiceDep,
):
    return await task_service.create_task(
        current_user=current_user,
        title=task.title,
        description=task.description,
        project_id=task.project_id,
        status=task.status,
    )


@router.get(
    "/{task_id}",
    response_model=TaskDetailed,
)
async def get_task(
    task_id: int,
    current_user: CurrentUser,
    task_service: TaskServiceDep,
):
    return await task_service.get_task(
        current_user=current_user,
        task_id=task_id,
    )


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
)
async def update_task(
    task_id: int,
    task: TaskUpdate,
    current_user: CurrentUser,
    task_service: TaskServiceDep,
):
    return await task_service.update_task(
        current_user=current_user,
        task_id=task_id,
        title=task.title,
        description=task.description,
        status=task.status,
    )


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_task(
    task_id: int,
    current_user: CurrentUser,
    task_service: TaskServiceDep,
):
    await task_service.delete_task(
        current_user=current_user,
        task_id=task_id,
    )
