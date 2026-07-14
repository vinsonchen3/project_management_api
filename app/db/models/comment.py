from db.database import Base
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    date_posted: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    task_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False
    )

    # relationships
    author: Mapped["User"] = relationship(back_populates="comments") # type: ignore
    task: Mapped["Task"] = relationship(back_populates="comments") # type: ignore