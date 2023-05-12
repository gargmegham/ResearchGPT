import logging
from datetime import datetime

from sqlalchemy import (BIGINT, Column, DateTime, ForeignKey, String, Text,
                        UniqueConstraint)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from database import Base

logger = logging.getLogger(__name__)

Base = declarative_base()


class ChatRoom(Base):
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

    chatroom_messages = relationship("ChatRoomMessage", back_populates="chatroom")


class ChatRoomMessage(Base):
    """
    -- synthbot_db.chatroom_messages definition
        CREATE TABLE `chatroom_messages` (
        `id` bigint(20) NOT NULL AUTO_INCREMENT,
        `created_at` datetime DEFAULT NULL,
        `updated_at` datetime DEFAULT NULL,
        `chatroom_id` bigint(20) NOT NULL,
        `user_id` bigint(20) unsigned NOT NULL,
        `message` text NOT NULL,
        PRIMARY KEY (`id`),
        KEY `chatroom_messages_FK` (`chatroom_id`),
        KEY `chatroom_messages_FK_1` (`user_id`),
        CONSTRAINT `chatroom_messages_FK` FOREIGN KEY (`chatroom_id`) REFERENCES `chatrooms` (`id`)
        ) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
    """

    __tablename__ = "chatroom_messages"

    id = Column(BIGINT, primary_key=True, autoincrement=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    chatroom_id = Column(BIGINT, ForeignKey("chatrooms.id"))
    user_id = Column(BIGINT, nullable=False)
    message = Column(Text, nullable=False)

    chatroom = relationship("ChatRoom", back_populates="chatroom_messages")
