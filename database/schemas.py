from pydantic import BaseModel

from app.globals import SECRET_KEY


class Message(BaseModel):
    data: str
    typing: bool = False
    retry: int = None
    event: str = "message"


class MessageCreate(BaseModel):
    input: str
    chatroom_id: int


class User(BaseModel):
    username: str
    password: str


class Settings(BaseModel):
    authjwt_secret_key: str = SECRET_KEY
    authjwt_token_location: set = {"cookies"}
    authjwt_cookie_csrf_protect: bool = False


class ChatRoomBase(BaseModel):
    id: int
    user_id: int
    title: str
    search: str


class ChatRoomMessageBase(BaseModel):
    id: int
    chatroom_id: int
    user_id: int
    message: str


class ChatRoomMessageCreate(BaseModel):
    chatroom_id: int
    user_id: int
    message: str


class ChatRoomMessageUpdate(BaseModel):
    message: str


class ChatRoomMessageDelete(BaseModel):
    id: int


class ChatRoomCreate(BaseModel):
    search: str


class ChatRoomUpdate(BaseModel):
    title: str


class ChatRoom(ChatRoomBase):
    class Config:
        orm_mode = True


class ChatRoomMessage(ChatRoomMessageBase):
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
