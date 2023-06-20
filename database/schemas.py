from pydantic import BaseModel


class ChatRoomCreate(BaseModel):
    """Chatroom create from search"""

    search: str
    title: str
    name: str


class ChatRoomUpdate(BaseModel):
    """Chatroom update title"""

    name: str


class Chatroom(BaseModel):
    """Chatroom"""

    id: int
    user_id: int
    title: str
    search: str
    name: str

    class Config:
        orm_mode = True


class MessageFromWebsocket(BaseModel):
    """message from websocket"""

    msg: str
    chatroom_id: int


class InitMessage(BaseModel):
    """
    message to send to websocket on init
    """

    previous_chats: list[dict] | None = None
    chatroom_ids: list[int] | None = None
    init_callback: bool = True


class MessageToWebsocket(BaseModel):
    """
    message to send to websocket
        - msg: message to send
        - finish: whether the message is the last message
        - chatroom_id: chatroom id
        - is_user: whether the message is from user
        - init: whether the message is init message
        - model_name: model name
    """

    msg: str | None
    finish: bool
    chatroom_id: int
    is_user: bool
    init: bool = False
    model_name: str | None = None

    class Config:
        """
        orm_mode: whether to use orm mode
        """

        orm_mode = True


class SendToStream(BaseModel):
    """
    message to send to stream
        - role: role of the message
        - content: content of the message
    """

    role: str
    content: str

    class Config:
        orm_mode = True


class SendInitToWebsocket(BaseModel):
    """send init message to websocket"""

    content: str
    tokens: int
    is_user: bool
    timestamp: int
    model_name: str | None = None

    class Config:
        orm_mode = True
