import pytest
from collections.abc import AsyncGenerator

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.db.database import Base, get_db
from app.main import app
from app.core.config import settings

# anyio config

pytest_plugins = ["anyio"]


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


# test db and db session
@pytest.fixture(scope="session")
def test_engine():
    engine = create_async_engine(
        settings.test_database_url,
        poolclass=NullPool,
    )
    return engine


@pytest.fixture(scope="session")
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest.fixture
async def db_session(
    test_engine,
    setup_database,
) -> AsyncGenerator[AsyncSession]:
    connection = await test_engine.connect()
    transaction = await connection.begin()

    session_factory = async_sessionmaker(
        bind=connection,
        class_=AsyncSession,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    async with session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()
            await connection.close()


@pytest.fixture
async def client(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncClient]:

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as test_client:
        yield test_client
    app.dependency_overrides.clear()
