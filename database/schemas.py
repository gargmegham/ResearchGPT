from pydantic import BaseModel


class ChatRoomCreate(BaseModel):
    search: str


class ChatRoomUpdate(BaseModel):
    title: str


class ChatRoom(BaseModel):
    id: int
    user_id: int
    title: str
    search: str

    class Config:
        orm_mode = True


class MessageFromWebsocket(BaseModel):
    msg: str
    chatroom_id: int


class InitMessage(BaseModel):
    previous_chats: list[dict] | None = None
    chatroom_ids: list[str] | None = None


class MessageToWebsocket(BaseModel):
    msg: str | None
    finish: bool
    chatroom_id: int
    is_user: bool
    init: bool = False
    model_name: str | None = None

    class Config:
        orm_mode = True


class SendToStream(BaseModel):
    role: str
    content: str

    class Config:
        orm_mode = True


class SendInitToWebsocket(BaseModel):
    content: str
    tokens: int
    is_user: bool
    timestamp: int
    model_name: str | None = None

    class Config:
        orm_mode = True
