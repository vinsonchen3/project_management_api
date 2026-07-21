from db.database import Base
from sqlalchemy import Table, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

project_user_association = Table(
    "project_user",
    Base.metadata,
    Column("project_id", ForeignKey("projects.id"), primary_key=True),
    Column("user_id", ForeignKey("users.id"), primary_key=True),
)


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    owner_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    owner: Mapped["User"] = relationship(  # type: ignore
        back_populates="owned_projects",
        foreign_keys=[owner_id],
    )
    members: Mapped[list["User"]] = relationship(  # type: ignore
        secondary=project_user_association,
        back_populates="projects",
    )
    tasks: Mapped[list["Task"]] = relationship(  # type: ignore
        back_populates="project",
        cascade="all, delete-orphan",
    )
