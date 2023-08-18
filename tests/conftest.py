import asyncio

import pytest
import pytest_asyncio
from mixer.backend.sqlalchemy import mixer
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, async_scoped_session
from sqlalchemy.orm import Session, declarative_base, scoped_session

from db import UserState, State, Base


#
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def _db_engine():
    engine = create_async_engine('sqlite+aiosqlite:///:memory:', echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture(scope='session')
async def _db_session_maker(_db_engine):
    return async_scoped_session(async_sessionmaker(_db_engine, expire_on_commit=False), scopefunc=asyncio.current_task)


@pytest.fixture
async def db_session(_db_session_maker):
    test_session = _db_session_maker(expire_on_commit=False)
    yield test_session

    await test_session.rollback()
    await test_session.close()


@pytest.fixture(params=[s.value for s in State])
async def user_state_in_db(request, db_session):
    user_state = mixer.blend(UserState, current_state=request.param)
    async with db_session.begin():
        db_session.add(user_state)
    return user_state
