from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.project import ProjectResponse
    from app.schemas.task import TaskResponse
    from app.schemas.comment import CommentResponse


class UserBase(BaseModel):
    username: str = Field(min_length=1, max_length=50, description="Unique username")
    email: EmailStr = Field(max_length=100, description="Valid email address")


class UserCreate(UserBase):
    password: str = Field(min_length=8, description="Password; minimum 8 characters")


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: EmailStr


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    # password: str | None = Field(default=None, min_length=8)


class UserDetailed(UserResponse):
    owned_projects: list["ProjectResponse"] = Field(default_factory=list)
    projects: list["ProjectResponse"] = Field(default_factory=list)
    tasks: list["TaskResponse"] = Field(default_factory=list)
    comments: list["CommentResponse"] = Field(default_factory=list)
