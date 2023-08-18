import pytest

from bot.state_machine import get_current_state
from db import State


class TestState:

    async def test_get_current_state_of_user_in_db(self, db_session, user_state_in_db):
        current_state = await get_current_state(user_id=user_state_in_db.user_id, session=db_session)
        assert current_state == user_state_in_db.current_state

    async def test_get_current_state_of_user_not_in_db(self, db_session):
        user_id_not_in_db = 1111
        current_state = await get_current_state(user_id=user_id_not_in_db, session=db_session)
        assert current_state == State.DEFAULT.value
