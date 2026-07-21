from pydantic import BaseModel, ConfigDict, Field

class ProjectBase(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None

class ProjectCreate(ProjectBase):
    pass 

class ProjectResponse(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int

class ProjectDetailed(ProjectResponse):
    owner: "UserResponse"
    members: list["UserResponse"] = []
    tasks: list["TaskResponse"] = []

from schemas.user import UserResponse
from schemas.task import TaskResponse

ProjectDetailed.model_rebuild()