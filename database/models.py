from datetime import datetime

from sqlalchemy import BIGINT, Column, DateTime, String, UniqueConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Chatroom(Base):
    __tablename__ = "chatrooms"

    id = Column(BIGINT, primary_key=True, autoincrement=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(BIGINT, nullable=False)
    title = Column(String(255), default="")
    search = Column(String(255), default="")
    name = Column(String(255), default="Untitled")

    __table_args__ = (UniqueConstraint("user_id", "search", name="unique_user_search"),)

    class Config:
        orm_mode = True
