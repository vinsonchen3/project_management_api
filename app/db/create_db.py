from db.database import engine, Base

from db.models.user import User
from db.models.task import Task
from db.models.comment import Comment
from db.models.project import Project


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
