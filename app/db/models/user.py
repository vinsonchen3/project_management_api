from db.database import Base
from db.models.task import user_task_association
from db.models.project import project_user_association
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(200), nullable=False)

    # relationships
    tasks: Mapped[list["Task"]] = relationship( # type: ignore
        secondary=user_task_association, back_populates="assignees"
    )
    comments: Mapped[list["Comment"]] = relationship( # type: ignore
        back_populates="author", cascade="all, delete-orphan"
    )

    #projects owned by this user
    owned_projects: Mapped[list["Project"]] = relationship( # type: ignore
        back_populates="owner",
        foreign_keys="Project.owner_id",
    )

    #projects this user is a member of 
    projects: Mapped[list["Project"]] = relationship( # type: ignore
        secondary=project_user_association,
        back_populates="members",
        lazy="selectin",
    )