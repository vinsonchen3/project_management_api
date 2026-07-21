from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import List
from db.enums import TaskStatus


class TaskBase(BaseModel):
    title: str = Field(default="Untitled", max_length=250)
    description: str | None = Field(default=None, description="Description of task")
    status: TaskStatus = Field(default="Not Started")


class TaskCreate(TaskBase):
    project_id: int


class TaskResponse(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int


class TaskDetailed(TaskResponse):
    model_config = ConfigDict(from_attributes=True)

    assignees: List["UserResponse"] = []
    comments: List["CommentResponse"] = []
    project: "ProjectResponse"

from schemas.user import UserResponse
from schemas.comment import CommentResponse
from schemas.project import ProjectResponse

TaskDetailed.model_rebuild()