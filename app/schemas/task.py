from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import List
from app.db.enums import TaskStatus
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.user import UserResponse
    from app.schemas.project import ProjectResponse
    from app.schemas.comment import CommentResponse


class TaskBase(BaseModel):
    title: str = Field(default="Untitled", max_length=250)
    description: str | None = Field(default=None, description="Description of task")
    status: TaskStatus = Field(default=TaskStatus.TO_DO)


class TaskCreate(TaskBase):
    project_id: int


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=250)
    description: str | None = None
    status: TaskStatus | None = None


class TaskResponse(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int


class TaskAssignment(BaseModel):
    user_id: int


class TaskDetailed(TaskResponse):
    assignees: List["UserResponse"] = Field(default_factory=list)
    comments: List["CommentResponse"] = Field(default_factory=list)
    project: "ProjectResponse"
