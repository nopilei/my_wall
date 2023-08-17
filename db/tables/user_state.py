import enum

from sqlalchemy import String, Enum, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped

from db.tables.base import Base


class State(enum.Enum):
    SUBSCRIBING = 'subscribing'
    SUBSCRIBED = 'subscribed'
    DEFAULT = 'default'


class UserState(Base):
    __tablename__ = 'user_state'
    user_id: Mapped[int] = mapped_column(primary_key=True)
    current_state: Mapped[State] = mapped_column(String(50), Enum(State))

    __table_args__ = (
        UniqueConstraint('user_id', 'current_state', name='user_state_unique'),
    )
