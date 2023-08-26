import random

import pytest
from unittest.mock import Mock

from mixer.backend.sqlalchemy import mixer
from db import UserState, State


@pytest.fixture(params=State)
async def user_state(request, db_session):
    user_state = mixer.blend(UserState, user_id=random.randint(1, 100),  current_state=request.param.value)
    async with db_session.begin():
        db_session.add(user_state)
    return user_state


@pytest.fixture
async def different_state(user_state):
    return [s for s in State if s.value != user_state.current_state][0].value


@pytest.fixture
async def event(user_state):
    fake_event = Mock()
    fake_event.peer_id.user_id = user_state.user_id
    return fake_event


@pytest.fixture
async def mock_session_for_state(_db_session_maker, monkeypatch):
    monkeypatch.setattr('bot.state_machine.Session', _db_session_maker)
