import pytest

class TestState:

    async def test_a(self, db_session):
        assert 1 == 1
