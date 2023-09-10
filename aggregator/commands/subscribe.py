import os

from telethon import events, utils, TelegramClient, errors
from telethon.events.common import EventBuilder
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.types import Channel, UpdateChannel, TypeInputPeer

import errors as bot_errors
from aggregator.commands.base import BaseCommand
from db.aggregator_db import add_subscribtion, get_all_channels


class SubscribeCommand(BaseCommand):
    """Subscribe user to provided channel by link."""

    async def handle(self):
        user_id, channel_link = self._parse_request(self._event)

        channel_input_entity = await self._get_input_entity(channel_link)
        await self._subscribe_user_to_channel(channel_input_entity, user_id)

    def _parse_request(self, event: EventBuilder):
        user_id, channel_link = event.peer_id.user_id, event.message.message.strip()
        return user_id, channel_link

    async def _get_input_entity(self, channel_link: str):
        # We have to be a participant of channel before fetching messages from it
        await self._join_channel(channel_link)

        channel_input_entity = await self._client.get_input_entity(channel_link)
        await self._check_is_not_chat(channel_input_entity)
        return channel_input_entity

    async def _check_is_not_chat(self, input_entity):
        channel: Channel = await self._client.get_entity(input_entity)

        # Ensure channel is not a chat
        if not channel.broadcast:
            raise bot_errors.UnsubscribableEntity('Нельзя подписаться на чат')

    async def _join_channel(self, channel_link: str):
        username_or_hash, is_private = utils.parse_username(channel_link)

        if username_or_hash is None and not is_private:
            raise bot_errors.InvalidLink
        elif is_private:
            await self._join_private_channel(username_or_hash, channel_link)
        else:
            await self._join_public_channel(username_or_hash)

    async def _join_private_channel(self, channel_hash: str, channel_link: str):
        try:
            await self._client(ImportChatInviteRequest(channel_hash))
        except (errors.InviteHashExpiredError, errors.InviteHashInvalidError) as err:
            raise bot_errors.UnknownChannel from err
        except errors.InviteRequestSentError:
            self._subscribe_when_accepted(channel_link)
            raise bot_errors.AwaitingAcception
        except errors.UserAlreadyParticipantError:
            pass

    async def _join_public_channel(self, username: str):
        try:
            await self._client(JoinChannelRequest(username))
        except ValueError as err:
            raise bot_errors.UnknownChannel from err

    def _subscribe_when_accepted(self, channel_link: str):
        @self._client.on(events.Raw(types=[UpdateChannel]))
        async def handler(event):
            channel_id = event.channel_id
            channel_by_id = await self._client.get_input_entity(channel_id)
            channel_by_link = await self._client.get_input_entity(channel_link)
            if channel_by_id == channel_by_link:
                await self._subscribe_user_to_channel(channel_by_id, self._event.peer_id.user_id)
                self._client.remove_event_handler(handler)

    async def _subscribe_user_to_channel(self, channel: TypeInputPeer, user_id: int):
        await add_subscribtion(user_id, channel.channel_id)
        self._client.add_event_handler(self._consume, events.NewMessage(chats=[channel]))

    @staticmethod
    async def _consume(event):
        await event.message.forward_to(os.environ['BOT_USER_NAME'])

    @classmethod
    async def load_subscribtions(cls, client: TelegramClient):
        for channel_id in await get_all_channels():
            client.add_event_handler(cls._consume, events.NewMessage(chats=[channel_id]))
