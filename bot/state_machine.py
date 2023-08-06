from typing import Optional

from telethon.events import StopPropagation

from db.tables.models.user_state import State, UserState


def state(input_state: State, output_state: Optional[State] = None):
    def wrapper(handler):
        async def wrapped_handler(*args, **kwargs):
            event = args[0]
            user_id = event.peer_id.user_id
            current_state, _ = await UserState.objects.aget_or_create(
                user_id=user_id,
                defaults={'current_state': State.DEFAULT}
            )
            current_state = current_state.current_state
            if current_state == input_state:
                try:
                    result = await handler(event)
                except StopPropagation:
                    if output_state:
                        await UserState.objects.filter(user_id=user_id).aupdate(current_state=output_state)
                    raise

                if output_state:
                    await UserState.objects.filter(user_id=user_id).aupdate(current_state=output_state)

                return result
            return handler
        return wrapped_handler
    return wrapper


async def set_state(event, target_state):
    await UserState.objects.filter(user_id=event.peer_id.user_id).aupdate(current_state=target_state)