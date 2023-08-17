import pytest

pytestmark = [pytest.mark.django_db]


class TestState:
    def test_a(self, user_state_default):
        assert 1 == 1
