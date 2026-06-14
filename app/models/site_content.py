# app/models/site_content.py

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Text

from app.core.database import Base


class SiteContent(Base):
    __tablename__ = "site_content"

    id = Column(Integer, primary_key=True)

    about_text = Column(Text)

    predictions = Column(Text)

    win_rate = Column(Text)

    roi = Column(Text)

    members = Column(Text)