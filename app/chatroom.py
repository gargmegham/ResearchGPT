from fastapi import APIRouter, Response

from database import repository, schemas

router = APIRouter()


@router.get("/")
async def root():
    return {"message": "Server is running..."}


@router.post("/chatroom/{user_id}", response_model=schemas.Chatroom)
async def create_chatroom(
    chatroom: schemas.ChatRoomCreate,
    user_id: str,
):
    return await repository.create_chatroom(chatroom=chatroom, user_id=int(user_id))


@router.put("/chatroom/{chatroom_id}/{user_id}")
async def update_chatroom(
    chatroom_id: int,
    user_id: str,
    chatroom: schemas.ChatRoomUpdate,
):
    await repository.update_chatroom_name(
        chatroom_id=chatroom_id, name=chatroom.name, user_id=int(user_id)
    )
    return Response(status_code=200)


@router.delete("/chatroom/{chatroom_id}/{user_id}")
async def delete_chatroom(
    chatroom_id: int,
    user_id: str,
):
    await repository.delete_chatroom(chatroom_id=chatroom_id, user_id=int(user_id))
    return Response(status_code=200)


@router.get("/chatroom/{user_id}", response_model=list[schemas.Chatroom])
async def get_chatrooms(
    user_id: str,
):
    return await repository.get_all_chatrooms(user_id=int(user_id))
