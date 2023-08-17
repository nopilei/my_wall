import os

from telethon import events, utils, TelegramClient
from telethon.errors import InviteHashExpiredError, InviteHashInvalidError, UserAlreadyParticipantError
from telethon.events.common import EventBuilder
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.types import Channel

from aggregator.commands.base import BaseCommand
from db.aggregator_db import add_subscribtion, get_all_channels
from errors import InvalidLink, UnknownChannel, UnsubscribableEntity


class SubscribeCommand(BaseCommand):
    """Subscribe user to provided channel by link."""

    async def handle(self):
        user_id, channel_link = self._parse_request(self._event)

        channel_input_entity = await self._get_input_entity(channel_link)
        await add_subscribtion(user_id, channel_input_entity.channel_id)
        self._client.add_event_handler(self._consume, events.NewMessage(chats=[channel_input_entity]))

    def _parse_request(self, event: EventBuilder):
        user_id, channel_link = event.peer_id.user_id, event.message.message.strip()
        return user_id, channel_link

    async def _get_input_entity(self, peer: str):
        # We have to be subscribed to channel before fetching messages from it
        await self._subscribe_to_channel(peer)

        channel_input_entity = await self._client.get_input_entity(peer)
        await self._check_is_not_chat(channel_input_entity)
        return channel_input_entity

    async def _check_is_not_chat(self, input_entity):
        channel: Channel = await self._client.get_entity(input_entity)

        # Ensure channel is not a chat
        if not channel.broadcast:
            raise UnsubscribableEntity('Нельзя подписаться на чат')

    async def _subscribe_to_channel(self, peer: str):
        username, is_private = utils.parse_username(peer)

        if username is None and not is_private:
            raise InvalidLink
        elif is_private:
            await self._subscribe_to_private_channel(username)
        else:
            await self._subscribe_to_public_channel(username)

    async def _subscribe_to_private_channel(self, channel_hash: str):
        try:
            await self._client(ImportChatInviteRequest(channel_hash))
        except (InviteHashExpiredError, InviteHashInvalidError) as err:
            raise UnknownChannel from err
        except UserAlreadyParticipantError:
            pass

    async def _subscribe_to_public_channel(self, username: str):
        try:
            await self._client(JoinChannelRequest(username))
        except ValueError as err:
            raise UnknownChannel from err

    @classmethod
    async def load_subscribtions(cls, client: TelegramClient):
        for channel_id in await get_all_channels():
            print(channel_id, 5432342)
            client.add_event_handler(cls._consume, events.NewMessage(chats=[channel_id]))
            # print(client.list_event_handlers(), 89)

    @staticmethod
    async def _consume(event):
        print(os.environ['BOT_USER_NAME'], 324234)
        await event.message.forward_to(os.environ['BOT_USER_NAME'])
