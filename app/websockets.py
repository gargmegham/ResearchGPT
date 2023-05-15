from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from app.logger import api_logger
from gpt.stream_manager import begin_chat
from gpt.websocket_manager import SendToWebsocket

router = APIRouter()


def get_user_id_websocket(websocket: WebSocket):
    """
    Dependency to get user_id
    """
    try:
        xsrf = websocket.headers["XSRF-TOKEN"]
        session = websocket.headers["pubtrawlr_session"]
        if xsrf and session:
            # TODO replace with actual authentication
            api_logger.info(
                f"User authenticated! XSRF-TOKEN={xsrf}; pubtrawlr_session={session};"
            )
        return 25
    except:
        return None


@router.websocket("/chat-socket/")
async def ws_chatgpt(
    websocket: WebSocket,
    user_id: int = Depends(get_user_id_websocket),
):
    try:
        await websocket.accept()
        await begin_chat(
            websocket=websocket,
            user_id=user_id,
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
