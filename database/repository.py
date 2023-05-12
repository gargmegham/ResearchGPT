import logging

from sqlalchemy.orm import Session

from database import models, schemas

logger = logging.getLogger(__name__)


def create_chatroom(db: Session, chatroom: schemas.ChatRoomCreate, user_id: int):
    db_chatroom = models.ChatRoom(user_id=user_id, search=chatroom.search)
    db.add(db_chatroom)
    db.commit()
    db.refresh(db_chatroom)
    return db_chatroom


def update_chatroom(
    db: Session, chatroom_id: int, chatroom: schemas.ChatRoomUpdate, user_id: int
):
    updated_instances = (
        db.query(models.ChatRoom)
        .filter_by(id=chatroom_id, user_id=user_id)
        .update({models.ChatRoom.title: chatroom.title})
    )
    if updated_instances == 0:
        raise Exception("Chatroom not found")
    elif updated_instances > 1:
        raise Exception("More than one chatroom found")
    db.commit()
    return None


def delete_chatroom(db: Session, chatroom_id: int, user_id: int) -> None:
    deleted_instances = (
        db.query(models.ChatRoom).filter_by(id=chatroom_id, user_id=user_id).delete()
    )
    if deleted_instances == 0:
        raise Exception("Chatroom not found")
    elif deleted_instances > 1:
        raise Exception("More than one chatroom found")
    db.commit()
    return


def get_chatrooms(db: Session, user_id: int) -> list:
    return db.query(models.ChatRoom).filter_by(user_id=user_id).all()


def get_chatroom(
    db: Session, chatroom_id: int, user_id: int, last_message_id: int = -1
):
    messages = (
        db.query(models.ChatRoomMessage)
        .filter_by(chatroom_id=chatroom_id, user_id=user_id)
        .order_by(models.ChatRoomMessage.id.desc())
    )
    if last_message_id > 0:
        messages = messages.filter(models.ChatRoomMessage.id > last_message_id)
    messages = messages.limit(10).all()
    return messages[::-1]


def create_message(db: Session, message: schemas.MessageCreate, user_id: int):
    # returns content for StreamingResponse
    pass
