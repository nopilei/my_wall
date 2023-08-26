from functools import wraps

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from telethon.events import StopPropagation

from db import Session, State, UserState


def state(input_state: State | str, output_state: State | str | None = None):
    input_state = input_state.value if isinstance(input_state, State) else input_state
    output_state = output_state.value if isinstance(output_state, State) else output_state

    def wrapper(handler):
        @wraps(handler)
        async def wrapped_handler(*args, **kwargs):
            event = args[0]
            user_id = event.peer_id.user_id

            async with Session() as session, session.begin():
                current_state = await get_current_state(session, user_id)
                if current_state.current_state == input_state:
                    try:
                        result = await handler(event)
                    except StopPropagation:
                        await update_state_if_needed(current_state, output_state)
                        await session.commit()
                        raise
                    else:
                        await update_state_if_needed(current_state, output_state)
                    return result

        return wrapped_handler
    return wrapper


async def update_state_if_needed(current_state, output_state):
    if output_state:
        current_state.current_state = output_state


async def get_current_state(session, user_id):
    try:
        instance = await (session.execute(select(UserState).filter_by(user_id=user_id)))
        instance = instance.scalar_one()
    except NoResultFound:
        instance = UserState(user_id=user_id, current_state=State.DEFAULT.value)
        session.add(instance)
    return instance
