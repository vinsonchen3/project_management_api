from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.project import Project
from app.db.models.user import User


class ProjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        *,
        name: str,
        description: str | None,
        owner: User,
    ) -> Project:
        project = Project(
            name=name,
            description=description,
            owner_id=owner.id,
        )

        project.members.append(owner)

        self.db.add(project)
        await self.db.flush()
        return project

    async def get_by_id(
        self,
        project_id: int,
    ) -> Project | None:
        stmt = select(Project).where(Project.id == project_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id_with_members(
        self,
        project_id: int,
    ) -> Project | None:
        result = await self.db.execute(
            select(Project)
            .options(selectinload(Project.members))
            .where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_with_tasks(
        self,
        project_id: int,
    ) -> Project | None:
        result = await self.db.execute(
            select(Project)
            .options(selectinload(Project.tasks))
            .where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Project]:
        stmt = select(Project).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id_detailed(
        self,
        project_id: int,
    ) -> Project | None:
        result = await self.db.execute(
            select(Project)
            .options(
                selectinload(Project.owner),
                selectinload(Project.members),
                selectinload(Project.tasks),
            )
            .where(Project.id == project_id)
        )

        return result.scalar_one_or_none()

    async def get_for_user(
        self,
        user_id: int,
    ) -> list[Project]:
        result = await self.db.execute(
            select(Project).where(Project.members.any(User.id == user_id))
        )
        return result.scalars().all()

    async def update(
        self,
        project: Project,
    ) -> Project:
        await self.db.flush()
        await self.db.refresh(project)
        return project

    async def delete(
        self,
        project: Project,
    ) -> None:
        await self.db.delete(project)
