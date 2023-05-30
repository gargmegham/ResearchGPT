import jwt
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.exceptions import ChatroomNotFound
from app.globals import DEBUG_MODE, DEFAULT_JWT_SECRET
from app.logger import api_logger
from gpt.stream_manager import ChatGptStreamManager

router = APIRouter()


@router.websocket("/chat")
async def ws_chatgpt(
    websocket: WebSocket,
):
    """
    Websocket endpoint for chat, which is used to send and receive messages
    """
    try:
        token = websocket.query_params.get("token")
        chatroom_id = int(websocket.query_params.get("chatroom_id"))
        try:
            options = {"verify_signature": False} if DEBUG_MODE else {}
            decoded = jwt.decode(
                token, DEFAULT_JWT_SECRET, algorithms=["HS256"], options=options
            )
        except jwt.ExpiredSignatureError as err:
            ...
        user_id = int(decoded["user_id"])
        await websocket.accept()
        await ChatGptStreamManager.begin_chat(
            websocket=websocket,
            user_id=user_id,
            chatroom_id=chatroom_id,
        )
    except ValueError:
        api_logger.error("Invalid user id.", exc_info=True)
    except ChatroomNotFound as exception:
        api_logger.error(exception, exc_info=True)
    except jwt.PyJWTError as err:
        api_logger.error(f"Invalid token error from pyjwt\n {err}")
        websocket.close()
    except WebSocketDisconnect:
        ...
    except Exception as exception:
        api_logger.error(exception, exc_info=True)
