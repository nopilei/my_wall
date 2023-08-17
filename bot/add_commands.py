from telethon import TelegramClient
from telethon.events import StopPropagation, NewMessage

from aggregator.aggregator import Aggregator
from aggregator.commands.subscribe import SubscribeCommand
from db.bot_db import get_user_subscribtions
from errors import TelegramError


async def add_commands(
        bot: TelegramClient,
        aggregator: Aggregator,
        aggregator_user_id: int,
):
    @bot.on(NewMessage(pattern='/sub', forwards=False))
    # @state(State.DEFAULT, State.SUBSCRIBING)
    async def _sub(event):
        await event.respond('Какой канал слушать?')
        raise StopPropagation

    @bot.on(NewMessage(forwards=False))
    # @state(State.SUBSCRIBING, State.DEFAULT)
    async def _get_channel_links(event):
        try:
            await aggregator.execute(SubscribeCommand, event)
        except TelegramError as err:
            await _show_error_for_user(event, err)
        else:
            await event.respond('Вы подписаны')
        raise StopPropagation

    @bot.on(NewMessage(from_users=[aggregator_user_id], forwards=True))
    async def _show_message_from_channel(event):

        channel_id = event.message.fwd_from.from_id.channel_id
        for subscribtion in await get_user_subscribtions(channel_id=channel_id):
            user = subscribtion.user_id
            await event.message.forward_to(user)
        raise StopPropagation

    @bot.on(NewMessage(forwards=False))
    # @state(State.DEFAULT)
    async def _default_reply(event):
        await event.respond('Введите одну из комманд')
        raise StopPropagation


async def _show_error_for_user(event, error: TelegramError):
    await event.respond(error.message)
