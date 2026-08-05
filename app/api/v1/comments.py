from fastapi import APIRouter, status

from app.auth.dependencies import CurrentUser
from app.dependencies import CommentServiceDep

from app.schemas.comment import (
    CommentUpdate,
    CommentResponse,
)

router = APIRouter(prefix="/comments", tags=["Comments"])


@router.get(
    "/{comment_id}",
    response_model=CommentResponse,
)
async def get_comment(
    comment_id: int,
    current_user: CurrentUser,
    comment_service: CommentServiceDep,
):
    return await comment_service.get_comment(
        current_user=current_user,
        comment_id=comment_id,
    )


@router.patch(
    "/{comment_id}",
    response_model=CommentResponse,
)
async def update_comment(
    comment_id: int,
    comment: CommentUpdate,
    current_user: CurrentUser,
    comment_service: CommentServiceDep,
):
    return await comment_service.update_comment(
        current_user=current_user,
        comment_id=comment_id,
        content=comment.content,
    )


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_comment(
    comment_id: int,
    current_user: CurrentUser,
    comment_service: CommentServiceDep,
):
    await comment_service.delete_comment(
        current_user=current_user,
        comment_id=comment_id,
    )
