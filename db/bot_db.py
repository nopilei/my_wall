from sqlalchemy import select

from db import Session, UserSubscribtion


async def get_user_subscribtions(channel_id: str):
    async with Session() as session:
        stmt = select(UserSubscribtion).where(UserSubscribtion.channel_id == channel_id)
        a = await session.scalars(stmt)
        print(a, 234)
        await session.commit()
        return a
