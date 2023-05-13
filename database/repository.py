from sqlalchemy.future import select

from database import db, models, schemas
from database.models import Base


async def create_chatroom(chatroom: schemas.ChatRoomCreate, user_id: int):
    async with db.session() as transaction:
        db_chatroom = models.ChatRoom(user_id=user_id, search=chatroom.search)
        transaction.add(db_chatroom)
        await transaction.commit()
        await transaction.refresh(db_chatroom)
        return db_chatroom


async def validate_id(id: int, model: Base) -> bool:
    async with db.session() as transaction:
        db_instance = await transaction.get(model, id)
        if db_instance is None:
            return False
        return True


async def update_chatroom(
    chatroom_id: int, chatroom: schemas.ChatRoomUpdate, user_id: int
):
    async with db.session() as transaction:
        chatroom = await transaction.get(models.ChatRoom, chatroom_id)
        if chatroom is None:
            raise Exception("Chatroom not found")
        chatroom.title = chatroom.title
        await transaction.commit()
    return None


async def delete_chatroom(chatroom_id: int, user_id: int) -> None:
    async with db.session() as transaction:
        chatroom = await transaction.get(models.ChatRoom, chatroom_id)
        if chatroom is None:
            raise Exception("Chatroom not found")
        await transaction.delete(chatroom)
        await transaction.commit()
    return


async def get_chatrooms(user_id: int) -> list:
    async with db.session() as transaction:
        q = select(models.ChatRoom).where(models.ChatRoom.user_id == user_id)
        result = await transaction.execute(q)
        return result.scalars().all()


async def get_chatroom(chatroom_id: int, user_id: int, last_message_id: int = -1):
    async with db.session() as transaction:
        q = (
            select(models.ChatRoomMessage)
            .where(
                models.ChatRoomMessage.chatroom_id == chatroom_id,
                models.ChatRoomMessage.user_id == user_id,
            )
            .order_by(models.ChatRoomMessage.id.desc())
        )
        if last_message_id > 0:
            q = q.where(models.ChatRoomMessage.id > last_message_id)
        q = q.limit(10)
        result = await transaction.execute(q)
        messages = [message for message in result.scalars().all()]
        return messages[::-1]
