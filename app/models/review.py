from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import DateTime

from app.core.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True)

    avatar = Column(String(255))
    author = Column(String(255))
    text = Column(Text)
    rating = Column(Integer)

    published_at = Column(DateTime, default=datetime.utcnow)