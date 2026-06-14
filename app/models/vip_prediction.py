from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import Boolean

from app.core.database import Base


class VipPrediction(Base):
    __tablename__ = "vip_predictions"

    id = Column(Integer, primary_key=True)

    league = Column(String(255))
    match_name = Column(String(255))
    match_date = Column(DateTime)

    team_1_logo = Column(String(255))
    team_2_logo = Column(String(255))

    is_active = Column(Boolean, default=True)