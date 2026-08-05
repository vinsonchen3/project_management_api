from fastapi import APIRouter, status

from app.auth.dependencies import CurrentUser
from app.dependencies import TaskServiceDep, CommentServiceDep

from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskAssignment,
    TaskResponse,
    TaskDetailed,
)
from app.schemas.comment import CommentResponse, CommentCreate

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


@router.post(
    "/{task_id}/assignees",
    response_model=TaskResponse,
)
async def assign_user(
    task_id: int,
    assignment: TaskAssignment,
    current_user: CurrentUser,
    task_service: TaskServiceDep,
):
    return await task_service.assign_user(
        current_user=current_user,
        task_id=task_id,
        user_id=assignment.user_id,
    )


@router.delete(
    "/{task_id}/assignees/{user_id}",
    response_model=TaskResponse,
)
async def remove_assignee(
    task_id: int,
    user_id: int,
    current_user: CurrentUser,
    task_service: TaskServiceDep,
):
    return await task_service.remove_assignee(
        current_user=current_user,
        task_id=task_id,
        user_id=user_id,
    )


@router.get(
    "/{task_id}/comments",
    response_model=list[CommentResponse],
)
async def get_comments(
    task_id: int,
    current_user: CurrentUser,
    task_service: TaskServiceDep,
):
    return await task_service.get_comments(
        current_user=current_user,
        task_id=task_id,
    )


@router.post(
    "/{task_id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    task_id: int,
    comment: CommentCreate,
    current_user: CurrentUser,
    comment_service: CommentServiceDep,
):
    return await comment_service.create_comment(
        current_user=current_user,
        content=comment.content,
        task_id=task_id,
    )
