from sqlalchemy import select, and_, insert
from sqlalchemy.dialects.sqlite import insert as sqlite_upsert

from db import async_session, UserSubscribtion


async def add_subscribtion(user_id: int, channel_id: int):
    async with async_session() as session:
        print(user_id, channel_id, 2342342)
        stmt = select(UserSubscribtion).where(and_(
            UserSubscribtion.channel_id == channel_id,
            UserSubscribtion.user_id == user_id,
        ))
        subscribtion = (await session.scalars(stmt)).first()
        print(subscribtion, 92992)
        if not subscribtion:
            stmt = insert(UserSubscribtion).values(channel_id=channel_id, user_id=user_id)
            await session.execute(stmt)
        await session.commit()


async def get_all_channels():
    async with async_session() as session:
        stmt = select(UserSubscribtion.channel_id).distinct()
        a = await session.scalars(stmt)
        await session.commit()
        print(a, 234)
        return a
