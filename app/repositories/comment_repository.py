from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models.comment import Comment


class CommentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        content: str,
        author_id: int,
        task_id: int,
    ) -> Comment:
        comment = Comment(
            content=content,
            author_id=author_id,
            task_id=task_id,
        )

        self.db.add(comment)
        await self.db.flush()
        # await self.db.refresh(comment)

        return comment

    async def get_by_id(self, comment_id: int) -> Comment | None:
        result = await self.db.execute(select(Comment).where(Comment.id == comment_id))
        return result.scalar_one_or_none()

    async def get_by_id_with_author(
        self,
        comment_id: int,
    ) -> Comment | None:

        result = await self.db.execute(
            select(Comment)
            .options(selectinload(Comment.author))
            .where(Comment.id == comment_id)
        )

        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Comment]:
        result = await self.db.execute(select(Comment).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_task_comments(
        self,
        task_id: int,
    ) -> list[Comment]:
        result = await self.db.execute(
            select(Comment).where(Comment.task_id == task_id)
        )
        return result.scalars().all()

    async def get_task_comments_with_authors(
        self,
        task_id: int,
    ) -> list[Comment]:

        result = await self.db.execute(
            select(Comment)
            .options(selectinload(Comment.author))
            .where(Comment.task_id == task_id)
        )

        return result.scalars().all()

    async def get_by_author(
        self,
        author_id: int,
    ) -> list[Comment]:
        result = await self.db.execute(
            select(Comment).where(Comment.author_id == author_id)
        )
        return result.scalars().all()

    async def update(self, comment: Comment) -> Comment:
        await self.db.flush()
        await self.db.refresh(comment)
        return comment

    async def delete(self, comment: Comment) -> None:
        await self.db.delete(comment)
        await self.db.flush()
