from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.project import Project


class ProjectRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        *,
        name: str,
        description: str | None,
        owner_id: int,
    ) -> Project:
        project = Project(
            name=name,
            description=description,
            owner_id=owner_id,
        )
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

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Project]:
        stmt = select(Project).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def delete(
        self,
        project: Project,
    ) -> None:
        await self.db.delete(project)
