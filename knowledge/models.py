from enum import unique

from sqlalchemy import Column, Integer, String, DateTime
from core.database import Base
import datetime


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    guid = Column(String)
    fullname = Column(String)
    scientometric_database = Column(String)
    document_count = Column(Integer)
    citation_count = Column(Integer)
    h_index = Column(Integer)
    url = Column(String)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
