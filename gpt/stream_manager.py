import asyncio

from fastapi import WebSocket, WebSocketDisconnect
from fastapi.concurrency import run_in_threadpool
from pydantic import ValidationError

from app.exceptions import (
    GptOtherException,
    GptTextGenerationException,
    GptTooMuchTokenException,
)
from app.logger import api_logger
from database.schemas import MessageFromWebsocket, MessageToWebsocket
from gpt.buffer import BufferedUserContext
from gpt.cache_manager import ChatGptCacheManager
from gpt.commands import command_handler, get_contexts_sorted_from_recent_to_past
from gpt.common import GptRoles
from gpt.fileloader import read_bytes_to_text
from gpt.message_manager import MessageManager
from gpt.vectorstore_manager import VectorStoreManager
from gpt.websocket_manager import HandleMessage, SendToWebsocket


async def begin_chat(
    websocket: WebSocket,
    user_id: int,
) -> None:
    buffer: BufferedUserContext = BufferedUserContext(
        user_id=user_id,
        websocket=websocket,
        sorted_contexts=await get_contexts_sorted_from_recent_to_past(
            user_id=user_id,
            chatroom_ids=await ChatGptCacheManager.get_all_chatrooms(user_id=user_id),
        ),
    )

    await SendToWebsocket.initiation_of_chat(
        buffer=buffer,
        send_chatroom_ids=True,
        send_previous_chats=True,
    )

    # loop until connection is closed
    while True:
        try:
            rcvd: dict = await websocket.receive_json()
            assert isinstance(rcvd, dict)
            if "filename" in rcvd:
                text: str = await run_in_threadpool(
                    read_bytes_to_text,
                    await websocket.receive_bytes(),
                    rcvd["filename"],
                )
                docs: list[str] = await VectorStoreManager.create_documents(text)
                await SendToWebsocket.message(
                    websocket=websocket,
                    msg=f"Successfully embedded documents. You uploaded file begins with...\n\n```{docs[0][:50]}```...",
                    chatroom_id=buffer.current_chatroom_id,
                )
                continue
            received: MessageFromWebsocket = MessageFromWebsocket(**rcvd)
            if received.chatroom_id != buffer.current_chatroom_id:
                # This is a message from another chatroom, interpreted as change of context, while ignoring message
                index: int | None = buffer.find_index_of_chatroom(received.chatroom_id)
                if index is None:
                    # if received chatroom_id is not in chatroom_ids
                    raise Exception(
                        f"Received chatroom_id {received.chatroom_id} is not in chatroom_ids {buffer.sorted_chatroom_ids}"
                    )
                else:
                    # if received chatroom_id is in chatroom_ids, get context from memory
                    buffer.change_context_to(index=index)
                    await SendToWebsocket.initiation_of_chat(
                        buffer=buffer,
                        send_previous_chats=True,
                        send_chatroom_ids=False,
                    )
                continue
            if received.msg.startswith("/"):
                splitted: list[str] = received.msg[1:].split(" ")
                await command_handler(
                    callback_name=splitted[0],
                    callback_args=splitted[1:],
                    received=received,
                    websocket=websocket,
                    buffer=buffer,
                )
                continue
            await HandleMessage.user(
                msg=received.msg,
                buffer=buffer,
            )
            await HandleMessage.gpt(
                buffer=buffer,
            )
        except WebSocketDisconnect:
            # if websocket is disconnected, remove user from chatroom
            raise WebSocketDisconnect(code=1000, reason="client disconnected")
        except (AssertionError, ValidationError):
            # if message is not in the correct format, send error message to websocket and continue to next loop
            await SendToWebsocket.message(
                websocket=websocket,
                msg="Invalid message. Message is not in the correct format, maybe frontend - backend version mismatch?",
                chatroom_id=buffer.current_chatroom_id,
            )
            continue
        except ValueError as e:
            # if file type is not supported, send error message to websocket and continue to next loop
            api_logger.error(e, exc_info=True)
            await SendToWebsocket.message(
                websocket=websocket,
                msg="Invalid file type.",
                chatroom_id=buffer.current_chatroom_id,
            )
            continue
        except GptTextGenerationException:
            # if text generation fails, send error message to websocket and remove message history
            await asyncio.gather(
                SendToWebsocket.message(
                    websocket=websocket,
                    msg="Text generation failure. Please try again.",
                    chatroom_id=buffer.current_chatroom_id,
                ),
                MessageManager.pop_message_history_safely(
                    user_gpt_context=buffer.current_user_gpt_context,
                    role=GptRoles.USER,
                ),
            )
        except GptOtherException:
            # if other exception occurs, send error message to websocket and remove message history
            await asyncio.gather(
                SendToWebsocket.message(
                    websocket=websocket,
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
        except GptTooMuchTokenException as too_much_token_exception:
            # if user message is too long, send error message to websocket and continue to next loop
            await SendToWebsocket.message(
                websocket=websocket,
                msg=too_much_token_exception.msg
                if too_much_token_exception.msg is not None
                else "",
                chatroom_id=buffer.current_user_gpt_context.chatroom_id,
            )  # send too much token exception message to websocket
            continue
        except Exception as exception:
            # if other exception is raised (e.g. internal server error), log exception and send error message to websocket
            api_logger.error(f"chat exception: {exception}", exc_info=True)
            await websocket.send_json(  # finish stream message
                MessageToWebsocket(
                    msg="Internal Server Error",
                    finish=True,
                    chatroom_id=buffer.current_user_gpt_context.chatroom_id,
                    is_user=False,
                ).dict()
            )
            break
