from sqlalchemy.future import select

from app.exceptions import ChatroomNotFound
from database import db, models, schemas
from database.models import Base
from gpt.commands import create_new_chatroom, delete_old_chatroom


async def create_chatroom(chatroom: schemas.ChatRoomCreate, user_id: int):
    """Create a new chatroom in the database"""
    try:
        async with db.session() as transaction:
            db_chatroom = models.Chatroom(
                user_id=user_id, search=chatroom.search, title=chatroom.title
            )
            transaction.add(db_chatroom)
            await transaction.commit()
            await transaction.refresh(db_chatroom)
            create_new_chatroom(user_id, db_chatroom.id)
            return db_chatroom
    except Exception as e:
        raise Exception(f"Error creating chatroom ::: {e}")


async def validate_id(id: int, model: Base) -> bool:
    """Check if the id exists in the database"""
    async with db.session() as transaction:
        db_instance = await transaction.get(model, id)
        if db_instance is None:
            return False
        return True


async def update_chatroom_title(chatroom_id: int, title: str, user_id: int):
    """Update the title of a chatroom in the database"""
    async with db.session() as transaction:
        q = select(models.Chatroom).where(
            models.Chatroom.id == chatroom_id, models.Chatroom.user_id == user_id
        )
        result = await transaction.execute(q)
        chatroom = result.scalars().first()
        if chatroom is None:
            raise ChatroomNotFound()
        chatroom.title = title
        await transaction.commit()
    return


async def delete_chatroom(chatroom_id: int, user_id: int) -> None:
    """Delete a chatroom from the database"""
    async with db.session() as transaction:
        chatroom = await transaction.get(models.Chatroom, chatroom_id)
        if chatroom is None:
            raise ChatroomNotFound()
        await transaction.delete(chatroom)
        await transaction.commit()
        await delete_old_chatroom(chatroom_id, user_id)
    return


async def get_all_chatrooms(user_id: int) -> list:
    """Get all chatrooms from the database"""
    async with db.session() as transaction:
        q = select(models.Chatroom).where(models.Chatroom.user_id == user_id)
        result = await transaction.execute(q)
        return result.scalars().all()


async def get_chatroom(chatroom_id: int) -> models.Chatroom:
    """Get a chatroom from the database"""
    async with db.session() as transaction:
        q = select(models.Chatroom).where(models.Chatroom.id == chatroom_id)
        result = await transaction.execute(q)
        result = result.scalars().first()
        if result is None:
            raise ChatroomNotFound()
        return result
