import pytest
from mixer.backend.sqlalchemy import mixer
from db import UserState, State


@pytest.fixture
def user_state_default():
    return mixer.blend(UserState, current_state=State.DEFAULT)
