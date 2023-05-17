from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.auth import decrypt_aes_256_cbc
from app.exceptions import InvalidToken
from app.logger import api_logger
from gpt.stream_manager import ChatGptStreamManager
from gpt.websocket_manager import SendToWebsocket

router = APIRouter()


def get_user_id_websocket(websocket: WebSocket):
    """
    Dependency to get user_id and authenticate user
    """
    try:
        spark_token = websocket.headers["spark_token"]
        return decrypt_aes_256_cbc(spark_token)
    except (InvalidToken, Exception):
        return None


@router.websocket("/chat")
async def ws_chatgpt(
    websocket: WebSocket,
    user_id: int = Depends(get_user_id_websocket),
):
    """
    Websocket endpoint for chat, which is used to send and receive messages
    """
    try:
        if user_id is None:
            raise InvalidToken()
        await websocket.accept()
        await ChatGptStreamManager.begin_chat(
            websocket=websocket,
            user_id=user_id,
        )
    except InvalidToken:
        api_logger.error("Invalid token", exc_info=True)
        await SendToWebsocket.message(
            websocket=websocket,
            msg="Invalid token. close the connection.",
            chatroom_id=0,
        )
    except ValueError as exception:
        api_logger.error(exception, exc_info=True)
        await SendToWebsocket.message(
            websocket=websocket,
            msg=f"Chatroom not found. close the connection. ({exception})",
            chatroom_id=0,
        )
    except WebSocketDisconnect:
        ...
    except Exception as exception:
        api_logger.error(exception, exc_info=True)
        await SendToWebsocket.message(
            websocket=websocket,
            msg=f"An unknown error has occurred. close the connection. ({exception})",
            chatroom_id=0,
        )
