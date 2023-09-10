from functools import wraps

from db.engine import Session


def with_session(db_handler):
    @wraps(db_handler)
    async def make_calls_with_session(*args, **kwargs):
        async with Session.begin() as session:
            make_calls_with_session.session = session
            return await db_handler(*args, **kwargs)

    return make_calls_with_session
