import asyncio
import time
from typing import Type, Callable

from telethon import TelegramClient, errors

from aggregator.commands.base import BaseCommand
from aggregator.commands.subscribe import SubscribeCommand


class Aggregator:
    def __init__(
            self,
            session_name: str,
            api_id: int,
            api_hash: str,
            phone: str,
            code_callback: Callable[[], str] | None = None
    ):

        self.client = TelegramClient(session_name, api_id, api_hash)
        self._phone = phone
        self._code_callback = code_callback

    async def start(self):
        if not asyncio.get_event_loop().is_running():
            raise ValueError('You must run .start() in running event loop!')

        while True:
            try:
                await self.client.start(phone=self._phone, code_callback=self._code_callback)
            except errors.FloodWaitError as e:
                print('Have to sleep', e.seconds, 'seconds')
                time.sleep(e.seconds)
            else:
                break
        await SubscribeCommand.load_subscribtions(self.client)
        return self.client.run_until_disconnected()

    async def get_user_id(self) -> int:
        user = await self.client.get_me()
        print(user.stringify())
        return user.id

    async def execute(self, command: Type[BaseCommand], event):
        return await command(event, self.client).handle()
