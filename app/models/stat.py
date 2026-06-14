from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Date

from app.core.database import Base


class Stat(Base):
    __tablename__ = "stats"

    id = Column(Integer, primary_key=True)

    category = Column(String(20))      # free / paid

    match_date = Column(Date)

    sport = Column(String(100))

    event = Column(String(255))

    prediction = Column(String(255))

    odds = Column(String(20))

    result = Column(String(20))        # win / lose