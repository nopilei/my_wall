import asyncio
import os

from dotenv import load_dotenv

from db.setup_db import setup_db


async def run():
    load_dotenv()
    setup_db()

    from aggregator.aggregator import Aggregator
    from bot.bot import Bot

    aggregator = Aggregator(
        session_name=os.environ['AGGREGATOR_SESSIO_NAME'],
        api_id=int(os.environ['AGGREGATOR_API_ID']),
        api_hash=os.environ['AGGREGATOR_API_HASH'],
        phone=os.environ['AGGREGATOR_PHONE_NUMBER'],
        code=os.environ['AGGREGATOR_CODE'],
    )

    bot = Bot(
        session_name=os.environ['BOT_SESSION_NAME'],
        api_id=int(os.environ['BOT_API_ID']),
        api_hash=os.environ['BOT_API_HASH'],
        bot_token=os.environ['BOT_TOKEN'],
        aggregator=aggregator
    )

    if os.environ['ENVIRONMENT'] == 'dev':
        bot.bot.session.set_dc(
            os.environ['DEV_DC_NUMBER'],
            os.environ['DEV_DC_IP'],
            os.environ['DEV_DC_PORT'],
        )
        aggregator.client.session.set_dc(
            os.environ['DEV_DC_NUMBER'],
            os.environ['DEV_DC_IP'],
            os.environ['DEV_DC_PORT'],
        )

    await bot.start()


if __name__ == '__main__':
    asyncio.run(run())
