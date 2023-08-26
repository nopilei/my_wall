import asyncio
import pytest

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    async_scoped_session,
    AsyncSession,
    AsyncEngine
)

from db import Base


@pytest.fixture(scope="session")
def event_loop() -> asyncio.AbstractEventLoop:
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def _db_engine() -> AsyncEngine:
    engine = create_async_engine('sqlite+aiosqlite:///:memory:', echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope='session')
async def _db_session_maker(_db_engine: AsyncEngine) -> async_scoped_session[AsyncSession]:
    session_maker = async_sessionmaker(_db_engine, expire_on_commit=False)
    session_maker = async_scoped_session(session_maker, scopefunc=asyncio.current_task)
    return session_maker


@pytest.fixture
async def db_session(_db_engine: AsyncEngine, _db_session_maker: async_scoped_session[AsyncSession]) -> AsyncSession:
    async with _db_engine.begin() as conn:
        await conn.execute(text('PRAGMA foreign_keys = 0;'))
        for table in Base.metadata.sorted_tables:
            await conn.execute(table.delete())
        await conn.execute(text('PRAGMA foreign_keys = 1;'))

    test_session: AsyncSession = _db_session_maker(expire_on_commit=False)
    yield test_session

    await test_session.rollback()
    await test_session.close()
