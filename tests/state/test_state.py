from unittest.mock import AsyncMock

import pytest
from telethon.events import StopPropagation

from bot.state_machine import get_current_state, state
from db import State, UserState


class TestStateUtils:
    async def test_update_state(self, db_session, user_state):
        current_state = await get_current_state(user_id=user_state.user_id, session=db_session)
        assert current_state.current_state == user_state.current_state

    async def test_get_current_state_of_user_in_db(self, db_session, user_state):
        current_state = await get_current_state(user_id=user_state.user_id, session=db_session)
        assert current_state.current_state == user_state.current_state

    async def test_get_current_state_of_user_not_in_db(self, db_session):
        user_id_not_in_db = 1111
        current_state = await get_current_state(user_id=user_id_not_in_db, session=db_session)
        assert current_state.current_state == State.DEFAULT.value


@pytest.mark.usefixtures('mock_session_for_state')
class TestState:
    async def test_state_changed_from_input_state(
            self,
            db_session,
            faker,
            different_state,
            user_state: UserState,
            event,
    ):
        handler = AsyncMock(return_value=faker.name())
        wrapped_handler = state(user_state.current_state, different_state)(handler)
        result = await wrapped_handler(event)
        async with db_session.begin():
            await db_session.refresh(user_state)

        assert user_state.current_state == different_state
        assert result == handler.return_value

    async def test_state_is_not_allowed(
            self,
            db_session,
            different_state,
            user_state: UserState,
            event
    ):
        old_state = user_state.current_state
        handler = AsyncMock()
        wrapped_handler = state(different_state)(handler)
        await wrapped_handler(event)
        async with db_session.begin():
            await db_session.refresh(user_state)

        assert user_state.current_state == old_state
        handler.assert_not_called()

    async def test_state_changes_when_stop_propagation_raised(
            self,
            db_session,
            different_state,
            user_state: UserState,
            event
    ):
        handler = AsyncMock(side_effect=StopPropagation)
        wrapped_handler = state(user_state.current_state, different_state)(handler)

        with pytest.raises(StopPropagation):
            await wrapped_handler(event)
        async with db_session.begin():
            await db_session.refresh(user_state)
        assert user_state.current_state == different_state

    async def test_state_remains_unchanged_when_other_exception_raised(
            self,
            db_session,
            different_state,
            user_state: UserState,
            event
    ):
        old_state = user_state.current_state
        handler = AsyncMock(side_effect=Exception)
        wrapped_handler = state(user_state.current_state, different_state)(handler)

        with pytest.raises(Exception):
            await wrapped_handler(event)
        async with db_session.begin():
            await db_session.refresh(user_state)
        assert user_state.current_state == old_state
