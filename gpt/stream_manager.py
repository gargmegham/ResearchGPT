import asyncio

from fastapi import WebSocket, WebSocketDisconnect
from orjson import JSONDecodeError
from orjson import loads as orjson_loads
from pydantic import ValidationError

from app.exceptions import (
    GptException,
    GptInterruptedException,
    GptOtherException,
    ChatroomNotFound,
    GptTextGenerationException,
    GptTooMuchTokenException,
    MySQLConnectionError,
)
from app.logger import api_logger
from database.schemas import MessageFromWebsocket
from gpt.buffer import BufferedUserContext
from gpt.cache_manager import ChatGptCacheManager
from gpt.commands import command_handler, get_contexts_sorted_from_recent_to_past
from gpt.common import GptRoles
from gpt.message_handler import MessageHandler
from gpt.message_manager import MessageManager
from gpt.vectorstore_manager import VectorStoreManager
from gpt.websocket_manager import SendToWebsocket


class ChatGptStreamManager:
    @classmethod
    async def begin_chat(cls, websocket: WebSocket, user_id: int) -> None:
        try:
            buffer: BufferedUserContext = BufferedUserContext(
                user_id=user_id,
                websocket=websocket,
                sorted_contexts=await get_contexts_sorted_from_recent_to_past(
                    user_id=user_id,
                    chatroom_ids=await ChatGptCacheManager.get_all_chatrooms(
                        user_id=user_id
                    ),
                ),
            )
        except ChatroomNotFound:
            await SendToWebsocket.message(
                websocket=websocket,
                msg="You have no chatrooms. Please create one.",
                chatroom_id="",
            )
            return
        except MySQLConnectionError:
            api_logger.error("MySQL connection error", exc_info=True)
            await SendToWebsocket.message(
                websocket=buffer.websocket,
                msg="MySQL connection error. Please try again.",
                chatroom_id=buffer.current_chatroom_id,
            )
        try:
            await SendToWebsocket.init(buffer=buffer)
            await asyncio.gather(
                cls._websocket_receiver(buffer=buffer),
                cls._websocket_sender(buffer=buffer),
            )
        except (
            GptOtherException,
            GptTextGenerationException,
            GptTooMuchTokenException,
        ) as e:
            api_logger.error(e)
            await SendToWebsocket.message(
                websocket=buffer.websocket,
                msg="An error occurred. Please try again.",
                chatroom_id=buffer.current_chatroom_id,
            )
        except WebSocketDisconnect:
            return
        except RuntimeError:
            return
        except Exception as e:
            api_logger.error(f"Exception in chat: {e}", exc_info=True)
            await SendToWebsocket.message(
                websocket=buffer.websocket,
                msg="Internal server error. Please try again.",
                chatroom_id=buffer.current_chatroom_id,
            )

    @staticmethod
    async def _websocket_receiver(buffer: BufferedUserContext) -> None:
        filename: str = ""
        # loop until connection is closed
        while True:
            rcvd = await buffer.websocket.receive()
            received_text: str | None = rcvd.get("text")
            received_bytes: bytes | None = rcvd.get("bytes")
            if received_text is not None:
                try:
                    received_json: dict = orjson_loads(received_text)
                    assert isinstance(received_json, dict)
                except (JSONDecodeError, AssertionError):
                    if received_text == "stop":
                        buffer.done.set()
                else:
                    try:
                        await buffer.queue.put(MessageFromWebsocket(**received_json))
                    except ValidationError:
                        if "filename" in received_json:
                            filename = received_json["filename"]
            elif received_bytes is not None:
                await buffer.queue.put(
                    await VectorStoreManager.embed_file_to_vectorstore(
                        file=received_bytes, filename=filename
                    )
                )

    @classmethod
    async def _websocket_sender(cls, buffer: BufferedUserContext) -> None:
        # loop until connection is closed
        while True:
            try:
                item: MessageFromWebsocket | str = await buffer.queue.get()
                if isinstance(item, str):
                    await SendToWebsocket.message(
                        websocket=buffer.websocket,
                        msg=item,
                        chatroom_id=buffer.current_chatroom_id,
                    )
                elif isinstance(item, MessageFromWebsocket):
                    if item.chatroom_id != buffer.current_chatroom_id:
                        # This is a message from another chat room, interpreted as change of context, while ignoring message
                        await cls._change_context(
                            buffer=buffer,
                            changed_chatroom_id=item.chatroom_id,
                        )
                    elif item.msg.startswith("/"):
                        # if user message is command, handle command
                        splitted: list[str] = item.msg[1:].split(" ")
                        await command_handler(
                            callback_name=splitted[0],
                            callback_args=splitted[1:],
                            buffer=buffer,
                        )
                    else:
                        await MessageHandler.user(
                            msg=item.msg,
                            buffer=buffer,
                        )
                        await MessageHandler.gpt(
                            buffer=buffer,
                        )
            except GptException as gpt_exception:
                await cls._gpt_exception_handler(
                    buffer=buffer, gpt_exception=gpt_exception
                )

    @staticmethod
    async def _change_context(
        buffer: BufferedUserContext, changed_chatroom_id: str
    ) -> None:
        index: int | None = buffer.find_index_of_chatroom(changed_chatroom_id)
        if index is None:
            raise Exception(
                f"Received chatroom_id {buffer.current_chatroom_id} is not in chatroom_ids {buffer.sorted_chatroom_ids}"
            )
        else:
            # if received chatroom_id is in chatroom_ids, get context from memory
            buffer.change_context_to(index=index)
            await SendToWebsocket.init(
                buffer=buffer,
                send_chatroom_ids=False,
            )

    @staticmethod
    async def _gpt_exception_handler(
        buffer: BufferedUserContext, gpt_exception: GptException
    ):
        if isinstance(gpt_exception, GptTextGenerationException):
            await asyncio.gather(
                SendToWebsocket.message(
                    websocket=buffer.websocket,
                    msg="Text generation failure. Please try again.",
                    chatroom_id=buffer.current_chatroom_id,
                ),
                MessageManager.pop_message_history_safely(
                    user_gpt_context=buffer.current_user_gpt_context,
                    role=GptRoles.USER,
                ),
            )
        elif isinstance(gpt_exception, GptInterruptedException):
            await MessageManager.pop_message_history_safely(
                user_gpt_context=buffer.current_user_gpt_context,
                role=GptRoles.USER,
            )
        elif isinstance(gpt_exception, GptOtherException):
            await asyncio.gather(
                SendToWebsocket.message(
                    websocket=buffer.websocket,
                    msg="Something's wrong. Please try again.",
                    chatroom_id=buffer.current_chatroom_id,
                ),
                MessageManager.pop_message_history_safely(
                    user_gpt_context=buffer.current_user_gpt_context,
                    role=GptRoles.USER,
                ),
                MessageManager.pop_message_history_safely(
                    user_gpt_context=buffer.current_user_gpt_context,
                    role=GptRoles.GPT,
                ),
            )
        elif isinstance(gpt_exception, GptTooMuchTokenException):
            # send too much token exception message to websocket
            await SendToWebsocket.message(
                websocket=buffer.websocket,
                msg=gpt_exception.msg if gpt_exception.msg is not None else "",
                chatroom_id=buffer.current_user_gpt_context.chatroom_id,
            )
