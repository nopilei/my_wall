from functools import wraps
from collections.abc import Callable, Awaitable
from typing import ParamSpec

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from telethon.events import StopPropagation

from db import Session, State, UserState

P = ParamSpec('P')
THandler = Callable[P, Awaitable]


def state(input_state: State | str, output_state: State | str | None = None) -> Callable[[THandler], THandler]:
    input_state = input_state.value if isinstance(input_state, State) else input_state
    output_state = output_state.value if isinstance(output_state, State) else output_state

    def wrapper(handler: THandler) -> THandler:
        @wraps(handler)
        async def wrapped_handler(*args: P.args, **kwargs: P.args) -> Awaitable:
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


async def update_state_if_needed(current_state: UserState, output_state: str) -> None:
    if output_state:
        current_state.current_state = output_state


async def get_current_state(session: AsyncSession, user_id: int) -> UserState:
    try:
        instance = await (session.execute(select(UserState).filter_by(user_id=user_id)))
        instance = instance.scalar_one()
    except NoResultFound:
        instance = UserState(user_id=user_id, current_state=State.DEFAULT.value)
        session.add(instance)
    return instance
