from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped

from db.tables.base import Base


class UserSubscribtion(Base):
    __tablename__ = 'user_subscribtion'

    user_id: Mapped[int] = mapped_column(primary_key=True)
    channel_id: Mapped[int] = mapped_column(primary_key=True)

    __table_args__ = (
        UniqueConstraint('user_id', 'channel_id', name='user_subscribtion_unique'),
    )
