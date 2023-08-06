from telethon import TelegramClient
from telethon.events.common import EventBuilder


class BaseCommand:
    def __init__(self, event: EventBuilder,  client: TelegramClient):
        self._client = client
        self._event = event

    async def handle(self):
        raise NotImplementedError
