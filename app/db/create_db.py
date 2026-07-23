from app.db.database import engine, Base

from app.db.models.user import User
from app.db.models.task import Task
from app.db.models.comment import Comment
from app.db.models.project import Project


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
