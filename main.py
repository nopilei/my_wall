import argparse
import asyncio
import os

from dotenv import load_dotenv

from aggregator.aggregator import Aggregator
from bot.bot import Bot


async def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--env', choices=['dev', 'prod'], required=True)
    env = parser.parse_args().env

    load_dotenv('dev.env' if env == 'dev' else 'prod.env')
    aggregator = Aggregator(
        session_name=os.environ['AGGREGATOR_SESSION_NAME'],
        api_id=int(os.environ['AGGREGATOR_API_ID']),
        api_hash=os.environ['AGGREGATOR_API_HASH'],
        phone=os.environ['AGGREGATOR_PHONE_NUMBER'],
    )

    bot = Bot(
        session_name=os.environ['BOT_SESSION_NAME'],
        api_id=int(os.environ['BOT_API_ID']),
        api_hash=os.environ['BOT_API_HASH'],
        bot_token=os.environ['BOT_TOKEN'],
        aggregator=aggregator
    )

    await bot.start()


if __name__ == '__main__':
    asyncio.run(run())
