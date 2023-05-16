from datetime import datetime

from sqlalchemy import BIGINT, Column, DateTime, String, UniqueConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Chatroom(Base):
    """
    -- synthbot_db.chatrooms definition
        CREATE TABLE `chatrooms` (
        `id` bigint(20) NOT NULL AUTO_INCREMENT,
        `created_at` datetime DEFAULT NULL,
        `updated_at` datetime DEFAULT NULL,
        `user_id` bigint(20) unsigned NOT NULL,
        `title` varchar(255) DEFAULT 'Untitled',
        `search` varchar(255) DEFAULT '',
        PRIMARY KEY (`id`),
        UNIQUE KEY `unique_user_search` (`user_id`,`search`)
        ) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
    """

    __tablename__ = "chatrooms"

    id = Column(BIGINT, primary_key=True, autoincrement=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(BIGINT, nullable=False)
    title = Column(String(255), default="Untitled")
    search = Column(String(255), default="")

    __table_args__ = (UniqueConstraint("user_id", "search", name="unique_user_search"),)
