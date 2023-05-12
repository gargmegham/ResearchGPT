import logging

from pydantic import BaseModel

from app.globals import SECRET_KEY

logger = logging.getLogger(__name__)


class Message(BaseModel):
    output: str
    typing: bool = False


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
