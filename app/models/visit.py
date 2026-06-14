from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import UniqueConstraint

from app.core.database import Base


class Visit(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True)

    ip = Column(String(100))
    user_agent = Column(String(500))
    device = Column(String(100))
    country = Column(String(100))
    country_code = Column(String(10))
    domain = Column(String(255))

    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("ip", "user_agent", name="unique_visit_ip_user_agent"),
    )