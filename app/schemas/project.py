from pydantic import BaseModel, ConfigDict, Field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.schemas.user import UserResponse
    from app.schemas.task import TaskResponse


class ProjectBase(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectResponse(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int


class ProjectUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150,
    )
    description: str | None = None


class ProjectDetailed(ProjectResponse):
    owner: "UserResponse"
    members: list["UserResponse"] = Field(default_factory=list)
    tasks: list["TaskResponse"] = Field(default_factory=list)
