from sqlalchemy import select, ScalarResult

from db.tables import UserSubscribtion
from db.utils import with_session


@with_session
async def get_user_subscribtions(channel_id: str) -> ScalarResult[UserSubscribtion]:
    stmt = select(UserSubscribtion).where(UserSubscribtion.channel_id == channel_id)
    return await get_user_subscribtions.session.scalars(stmt)
