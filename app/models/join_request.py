from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime

from app.core.database import Base


class JoinRequest(Base):
    __tablename__ = "join_requests"

    id = Column(Integer, primary_key=True)

    telegram_user_id = Column(String(100), unique=True)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    channel_title = Column(String(255))

    created_at = Column(DateTime, default=datetime.utcnow)