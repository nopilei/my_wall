import asyncio

from telethon import TelegramClient

from aggregator.aggregator import Aggregator
from bot.add_commands import add_commands


class Bot:
    def __init__(
            self,
            session_name: str,
            api_id: int,
            api_hash: str,
            bot_token: str,
            aggregator: Aggregator,
    ):
        self.bot_token = bot_token
        self.aggregator = aggregator
        self.bot = TelegramClient(session_name, api_id, api_hash)

    async def start(self):
        aggregator_task = await self.aggregator.start()

        await self.bot.start(bot_token=self.bot_token)
        user_id = await self.aggregator.get_user_id()
        await add_commands(self.bot, self.aggregator, user_id)

        bot_task = self.bot.run_until_disconnected()
        await asyncio.gather(aggregator_task, bot_task)
