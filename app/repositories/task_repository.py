from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models.task import Task


class TaskRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        title: str,
        description: str,
        status: str = "Not Started",
    ) -> Task:
        task = Task(
            title=title,
            description=description,
            status=status,
        )

        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)

        return task

    async def get_by_id(self, task_id: int) -> Task | None:
        result = await self.db.execute(select(Task).where(Task.id == task_id))
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Task]:
        result = await self.db.execute(select(Task).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_by_status(
        self,
        status: str,
    ) -> list[Task]:
        result = await self.db.execute(select(Task).where(Task.status == status))
        return result.scalars().all()

    async def update(self, task: Task) -> Task:
        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def delete(self, task: Task) -> None:
        await self.db.delete(task)
        await self.db.commit()
