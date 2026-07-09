from db.database import Base
from db.models.user import User
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
)
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
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(250), default="Untitiled")
    description: Mapped[str] = mapped_column(Text)
    # TODO: make status use enums for status codes insteaad of string
    status: Mapped[str] = mapped_column(String, default="Not Started")

    # relationships
    assignees: Mapped[list[User]] = relationship(
        User, secondary=user_task_association, back_populates="tasks"
    )
