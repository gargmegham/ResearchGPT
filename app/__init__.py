import builtins
import logging
import os
from functools import partial

from fastapi import Depends, FastAPI, Request, Response, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse

from app.dependencies import process_pool_executor
from app.exceptions import Responses_400
from app.globals import *
from database import SessionLocal, cache, repository, schemas
from gpt.stream_manager import begin_chat
from gpt.websocket_manager import SendToWebsocket

builtins.print = partial(print, flush=True)

logging.config.fileConfig("config/logging.conf", disable_existing_loggers=False)

from database import schemas

"""
Create directories if not exist
"""
os.makedirs(LOG_DIR, exist_ok=True)
with open(os.path.join(LOG_DIR, "bash.log"), "a") as f:
    pass
with open(os.path.join(LOG_DIR, "app.log"), "a") as f:
    pass

# get root logger
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ResearchGPT",
    description="ResearchGPT is a tool for researchers to generate ideas and insights.",
    version="0.1.0",
)

cache.start()


@app.on_event("startup")
async def startup():
    if cache.redis is None:
        raise ConnectionError("Redis is not connected yet!")
    if cache.is_initiated and await cache.redis.ping():
        logger.critical("Redis CACHE connected!")
    else:
        logger.critical("Redis CACHE connection failed!")


@app.on_event("shutdown")
async def shutdown():
    process_pool_executor.shutdown()
    await cache.close()
    logger.critical("DB & CACHE connection closed!")


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    return Response("Internal server error", status_code=500)


@app.middleware("http")
async def authentication_middle(request: Request, call_next):
    """
    Sample cookie: XSRF-TOKEN=; pubtrawlr_session=;
    """
    response = Response("Internal server error", status_code=500)
    try:
        xsrf = request.cookies.get("XSRF-TOKEN")
        session = request.cookies.get("pubtrawlr_session")
        if xsrf and session:
            # TODO replace with actual authentication
            TEMP_USER_ID = 25
            request.state.user_id = TEMP_USER_ID
            response = await call_next(request)
        elif request.url.path in ["/", "/docs", "/openapi.json", "/redoc"]:
            response = await call_next(request)
        else:
            response = Response("Unauthorized", status_code=401)
    finally:
        return response


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    except:
        response = Response("Internal server error", status_code=500)
    finally:
        request.state.db.close()
    return response


def get_db(request: Request):
    """
    Dependency to get db session
    """
    return request.state.db


def get_user_id(request: Request):
    """
    Dependency to get user_id
    """
    return request.state.user_id


def get_user_id_websocket(websocket: WebSocket):
    """
    Dependency to get user_id
    """
    return websocket.user_id


@app.get("/")
def root():
    return {"message": "Server is running..."}


@app.post("/chatroom/", response_model=schemas.ChatRoom)
def create_chatroom(
    chatroom: schemas.ChatRoomCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
):
    chatroom = repository.create_chatroom(db=db, chatroom=chatroom, user_id=user_id)
    return chatroom


@app.put("/chatroom/{chatroom_id}")
def update_chatroom(
    chatroom_id: int,
    chatroom: schemas.ChatRoomUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
):
    repository.update_chatroom(
        db=db, chatroom_id=chatroom_id, chatroom=chatroom, user_id=user_id
    )
    return Response(status_code=200)


@app.delete("/chatroom/{chatroom_id}")
def delete_chatroom(
    chatroom_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
):
    repository.delete_chatroom(db=db, chatroom_id=chatroom_id, user_id=user_id)
    return Response(status_code=200)


@app.get(
    "/chatroom/{chatroom_id}/{last_message_id}",
    response_model=list[schemas.ChatRoomMessage],
)
def get_chatroom(
    chatroom_id: int,
    last_message_id: int = -1,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
):
    chatroom = repository.get_chatroom(
        db=db, chatroom_id=chatroom_id, user_id=user_id, last_message_id=last_message_id
    )
    return chatroom


@app.get("/chatroom/", response_model=list[schemas.ChatRoom])
def get_chatrooms(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
):
    return repository.get_chatrooms(db=db, user_id=user_id)


@app.post("/chat/", response_model=schemas.Message)
def create_message(
    message: schemas.MessageCreate,
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_user_id),
):
    return EventSourceResponse(
        repository.create_message(request, db=db, message=message, user_id=user_id)
    )


@app.websocket("/chatgpt/{api_key}")
async def ws_chatgpt(
    websocket: WebSocket,
    user_id: int = Depends(get_user_id_websocket),
):
    if OPENAI_API_KEY is None:
        raise Responses_400.not_supported_feature
    try:
        await websocket.accept()  # accept websocket
        await begin_chat(
            websocket=websocket,
            user_id=25,
        )
    except WebSocketDisconnect:
        ...
    except Exception as exception:
        logger.error(exception, exc_info=True)
        await SendToWebsocket.message(
            websocket=websocket,
            msg=f"An unknown error has occurred. close the connection. ({exception})",
            chat_room_id="null",
        )
