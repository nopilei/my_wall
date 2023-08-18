from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from telethon.events import StopPropagation

from db import Session
from db.tables.user_state import State, UserState


def state(input_state: State, output_state: Optional[State] = None):
    def wrapper(handler):
        async def wrapped_handler(*args, **kwargs):
            event = args[0]
            user_id = event.peer_id.user_id

            async with Session() as session, session.begin():
                current_state = await get_current_state(session, user_id)
            if current_state == input_state:
                try:
                    result = await handler(event)
                except StopPropagation:
                    await update_state_id_needed(user_id, output_state)
                    raise
                else:
                    await update_state_id_needed(user_id, output_state)
                return result
            return handler

        return wrapped_handler

    return wrapper


async def update_state_id_needed(user_id, output_state):
    if output_state:
        await UserState.objects.filter(user_id=user_id).aupdate(current_state=output_state)


async def get_current_state(session, user_id):
    try:
        instance = await (session.execute(select(UserState).filter_by(user_id=user_id)))
        instance = instance.scalar_one()
    except NoResultFound:
        instance = UserState(user_id=user_id, current_state=State.DEFAULT.value)
        session.add(instance)
    return instance.current_state
