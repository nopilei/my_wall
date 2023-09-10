from unittest.mock import AsyncMock, Mock

import pytest
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession
from telethon.events import StopPropagation

from bot.state_machine import get_current_state, state
from db.tables import State, UserState


class TestStateUtils:
    async def test_update_state(self, db_session: AsyncSession, user_state: UserState):
        current_state = await get_current_state(user_id=user_state.user_id, session=db_session)
        assert current_state.current_state == user_state.current_state

    async def test_get_current_state_of_user_in_db(self, db_session: AsyncSession, user_state: UserState):
        current_state = await get_current_state(user_id=user_state.user_id, session=db_session)
        assert current_state.current_state == user_state.current_state

    async def test_get_current_state_of_user_not_in_db(self, db_session: AsyncSession):
        user_id_not_in_db = 1111
        current_state = await get_current_state(user_id=user_id_not_in_db, session=db_session)
        assert current_state.current_state == State.DEFAULT.value


@pytest.mark.usefixtures('mock_session_for_state')
class TestState:
    async def test_state_changed_from_input_state(
            self,
            db_session: AsyncSession,
            faker: Faker,
            different_state: str,
            user_state: UserState,
            event: Mock,
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
            db_session: AsyncSession,
            different_state: str,
            user_state: UserState,
            event: Mock
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
            db_session: AsyncSession,
            different_state: str,
            user_state: UserState,
            event: Mock
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
            db_session: AsyncSession,
            different_state: str,
            user_state: UserState,
            event: Mock
    ):
        old_state = user_state.current_state
        handler = AsyncMock(side_effect=Exception)
        wrapped_handler = state(user_state.current_state, different_state)(handler)

        with pytest.raises(Exception):
            await wrapped_handler(event)
        async with db_session.begin():
            await db_session.refresh(user_state)
        assert user_state.current_state == old_state
