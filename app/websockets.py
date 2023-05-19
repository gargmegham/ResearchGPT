from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.logger import api_logger
from app.exceptions import ChatroomNotFound
from gpt.stream_manager import ChatGptStreamManager
from gpt.websocket_manager import SendToWebsocket

router = APIRouter()


@router.websocket("/chat/{user_id}")
async def ws_chatgpt(
    websocket: WebSocket,
    user_id: str,
):
    """
    Websocket endpoint for chat, which is used to send and receive messages
    """
    try:
        user_id = int(user_id)
        await websocket.accept()
        await ChatGptStreamManager.begin_chat(
            websocket=websocket,
            user_id=user_id,
        )
    except ValueError:
        api_logger.error("Invalid user id.", exc_info=True)
        await SendToWebsocket.message(
            websocket=websocket,
            msg="Invalid user id. close the connection.",
            chatroom_id=0,
        )
    except ChatroomNotFound as exception:
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
