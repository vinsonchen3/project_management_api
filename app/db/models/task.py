from app.db.database import Base
from datetime import datetime
from sqlalchemy import (
    String,
    Integer,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    Table,
    Column,
    Enum,
)
from app.db.enums import TaskStatus
from sqlalchemy.orm import Mapped, mapped_column, relationship

user_task_association = Table(
    "user_task",
    Base.metadata,
    Column(
        "user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "task_id", Integer, ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True
    ),
)


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(250), default="Untitled")
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), default=TaskStatus.TO_DO, nullable=False
    )

    # relationships
    assignees: Mapped[list["User"]] = relationship(  # type: ignore
        secondary=user_task_association, back_populates="tasks"
    )
    comments: Mapped[list["Comment"]] = relationship(  # type: ignore
        back_populates="task", cascade="all, delete-orphan"
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    project: Mapped["Project"] = relationship(back_populates="tasks")  # type: ignore
