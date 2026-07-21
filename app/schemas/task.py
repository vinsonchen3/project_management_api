from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import List
from schemas.user import UserPublic
from schemas.comment import CommentPublic
from db.enums import TaskStatus

class TaskBase(BaseModel):
    title: str = Field(default="Untitled", max_length=250)
    description: str | None = Field(default=None, description="Description of task")
    status: TaskStatus = Field(default="Not Started")

class TaskCreate(TaskBase):
    pass 

class TaskResponse(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    id: int

class TaskDetailedResponse(TaskPublic):
    model_config = ConfigDict(from_attributes=True)

    assignees: List[UserPublic] = []
    comments: List[CommentPublic] = []

