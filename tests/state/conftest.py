import random

import pytest
from unittest.mock import Mock

from mixer.backend.sqlalchemy import mixer
from sqlalchemy.ext.asyncio import AsyncSession

from db.tables import State, UserState


@pytest.fixture(params=State)
async def user_state(request: pytest.FixtureRequest, db_session: AsyncSession) -> UserState:
    user_state = mixer.blend(UserState, user_id=random.randint(1, 100), current_state=request.param.value)
    async with db_session.begin():
        db_session.add(user_state)
    return user_state


@pytest.fixture
async def different_state(user_state: UserState) -> str:
    return [s for s in State if s.value != user_state.current_state][0].value


@pytest.fixture
async def event(user_state: UserState) -> Mock:
    fake_event = Mock()
    fake_event.peer_id.user_id = user_state.user_id
    return fake_event


@pytest.fixture
async def mock_session_for_state(_db_session_maker, monkeypatch) -> None:
    monkeypatch.setattr('bot.state_machine.Session', _db_session_maker)
