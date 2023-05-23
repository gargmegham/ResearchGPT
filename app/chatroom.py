from fastapi import APIRouter, Depends, Request, Response

from database import repository, schemas

router = APIRouter()


def get_user_id(request: Request):
    return request.state.user_id


@router.get("/")
async def root():
    return {"message": "Server is running..."}


@router.post("/chatroom", response_model=schemas.Chatroom)
async def create_chatroom(
    chatroom: schemas.ChatRoomCreate, user_id=Depends(get_user_id)
):
    return await repository.create_chatroom(chatroom=chatroom, user_id=int(user_id))


@router.put("/chatroom/{chatroom_id}")
async def update_chatroom(
    chatroom_id: int, chatroom: schemas.ChatRoomUpdate, user_id=Depends(get_user_id)
):
    await repository.update_chatroom_name(
        chatroom_id=chatroom_id, name=chatroom.name, user_id=int(user_id)
    )
    return Response(status_code=200)


@router.delete("/chatroom/{chatroom_id}")
async def delete_chatroom(chatroom_id: int, user_id=Depends(get_user_id)):
    await repository.delete_chatroom(chatroom_id=chatroom_id, user_id=int(user_id))
    return Response(status_code=200)


@router.get("/chatroom", response_model=list[schemas.Chatroom])
async def get_chatrooms(user_id=Depends(get_user_id)):
    return await repository.get_all_chatrooms(user_id=int(user_id))
