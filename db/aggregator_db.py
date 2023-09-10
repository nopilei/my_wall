from sqlalchemy import select, and_, ScalarResult

from db.tables import UserSubscribtion
from db.utils import with_session


@with_session
async def add_subscribtion(user_id: int, channel_id: int) -> None:
    stmt = select(UserSubscribtion).where(and_(
        UserSubscribtion.channel_id == channel_id,
        UserSubscribtion.user_id == user_id,
    ))
    subscribtion = (await add_subscribtion.session.scalars(stmt)).first()
    if not subscribtion:
        add_subscribtion.session.add(UserSubscribtion(channel_id=channel_id, user_id=user_id))


@with_session
async def get_all_channels() -> ScalarResult[UserSubscribtion]:
    stmt = select(UserSubscribtion.channel_id).distinct()
    return await get_all_channels.session.scalars(stmt)
