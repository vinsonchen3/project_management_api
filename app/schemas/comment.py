from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.user import UserResponse


class CommentBase(BaseModel):
    content: str = Field(min_length=1, description="Comment content")


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    content: str = Field(min_length=1)


class CommentResponse(CommentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date_posted: datetime
    author_id: int
    task_id: int


class CommentDetailed(CommentResponse):
    author: "UserResponse"
