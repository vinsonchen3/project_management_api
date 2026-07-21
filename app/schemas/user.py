from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from schemas.project import ProjectResponse
    from schemas.task import TaskResponse
    from schemas.comment import CommentResponse


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50, description="Unique username")
    email: EmailStr = Field(max_length=100, description="Valid email address")


class UserCreate(UserBase):
    password: str = Field(min_length=8, description="Password; minimum 8 characters")


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str


class UserDetailed(UserResponse):
    owned_projects: list["ProjectResponse"] = []
    projects: list["ProjectResponse"] = []
    tasks: list["TaskResponse"] = []
    comments: list["CommentResponse"] = []
