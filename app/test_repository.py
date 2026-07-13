import asyncio

from db.database import AsyncSessionLocal
from repositories.user_repository import UserRepository
from repositories.task_repository import TaskRepository



async def main():
    async with AsyncSessionLocal() as db:
        repo = UserRepository(db)
        repo2 = TaskRepository(db)

        user = await repo.create(
            username="balice",
            email="alice123@example.com",
            hashed_password="hashed_password",
        )

        task = await repo2.create(
            title="good title",
            description="hihiihiihi",
            status = "Not Started"
        )

        task.assignees.append(user)
        await db.flush()

        task = await repo2.get_by_id(task.id)

        print(task.assignees)

asyncio.run(main())