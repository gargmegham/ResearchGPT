import asyncio
from typing import AsyncGenerator, AsyncIterator, Generator, Iterator

from fastapi import WebSocket

from app.dependencies import process_manager, process_pool_executor
from app.exceptions import (
    GptModelNotImplementedException,
    GptTextGenerationException,
    GptTooMuchTokenException,
)
from gpt.buffer import BufferedUserContext
from gpt.generation import (
    generate_from_llama_cpp,
    generate_from_openai,
    message_history_organizer,
)
from gpt.llama_cpp import llama_cpp_generation
from gpt.message_manager import MessageManager
from gpt.models import (
    GptRoles,
    InitMessage,
    LlamaCppModel,
    MessageToWebsocket,
    OpenAIModel,
)


class SendToWebsocket:
    @staticmethod
    async def initiation_of_chat(
        websocket: WebSocket,
        buffer: BufferedUserContext,
    ) -> None:
        previous_chats = message_history_organizer(
            user_gpt_context=buffer.current_user_gpt_context,
            send_to_stream=False,
        )
        assert isinstance(previous_chats, list)
        await SendToWebsocket.message(
            websocket=websocket,
            msg=InitMessage(
                chatroom_ids=buffer.sorted_chatroom_ids,
                previous_chats=previous_chats,
            ).json(),
            chatroom_id=buffer.current_chatroom_id,
            init=True,
        )

    @staticmethod
    async def message(
        websocket: WebSocket,
        msg: str,
        chatroom_id: str,
        finish: bool = True,
        is_user: bool = False,
        init: bool = False,
    ) -> None:  # send whole message to websocket
        await websocket.send_json(  # send stream message
            MessageToWebsocket(
                msg=msg,
                finish=finish,
                chatroom_id=chatroom_id,
                is_user=is_user,
                init=init,
            ).dict()
        )

    @staticmethod
    async def stream(
        websocket: WebSocket,
        stream: AsyncGenerator | Generator | AsyncIterator | Iterator,
        chatroom_id: str,
        finish: bool = True,
        is_user: bool = False,
        chunk_size: int = 3,
        model_name: str | None = None,
    ) -> str:  # send whole stream to websocket
        final_response, stream_buffer = "", ""
        iteration: int = 0
        await websocket.send_json(
            MessageToWebsocket(
                msg=None,
                finish=False,
                chatroom_id=chatroom_id,
                is_user=is_user,
                model_name=model_name,
            ).dict()
        )
        if isinstance(stream, (Generator, Iterator)):
            for delta in stream:  # stream from local
                stream_buffer += delta
                iteration += 1
                if iteration % chunk_size == 0:
                    final_response += stream_buffer
                    await websocket.send_json(
                        MessageToWebsocket(
                            msg=stream_buffer,
                            finish=False,
                            chatroom_id=chatroom_id,
                            is_user=is_user,
                            model_name=model_name,
                        ).dict()
                    )
                    stream_buffer = ""
        elif isinstance(stream, (AsyncGenerator, AsyncIterator)):
            async for delta in stream:  # stream from api
                stream_buffer += delta
                iteration += 1
                if iteration % chunk_size == 0:
                    final_response += stream_buffer
                    await websocket.send_json(
                        MessageToWebsocket(
                            msg=stream_buffer,
                            finish=False,
                            chatroom_id=chatroom_id,
                            is_user=is_user,
                            model_name=model_name,
                        ).dict()
                    )
                    stream_buffer = ""
        else:
            raise TypeError("Stream type is not AsyncGenerator or Generator.")
        await websocket.send_json(
            MessageToWebsocket(
                msg=stream_buffer,
                finish=True if finish else False,
                chatroom_id=chatroom_id,
                is_user=is_user,
                model_name=model_name,
            ).dict()
        )
        return final_response


class HandleMessage:
    @staticmethod
    async def user(
        msg: str,
        buffer: BufferedUserContext,
    ) -> None:
        user_token: int = buffer.current_user_gpt_context.get_tokens_of(msg)
        if (
            user_token > buffer.current_user_gpt_context.token_per_request
        ):  # if user message is too long
            raise GptTooMuchTokenException(
                msg=f"Message too long. Now {user_token} tokens, but {buffer.current_user_gpt_context.token_per_request} tokens allowed."
            )
        await MessageManager.add_message_history_safely(
            user_gpt_context=buffer.current_user_gpt_context,
            content=msg,
            role=GptRoles.USER,
        )

    @staticmethod
    async def gpt(
        buffer: BufferedUserContext,
    ) -> None:
        try:
            if isinstance(buffer.current_user_gpt_context.gpt_model.value, OpenAIModel):
                msg: str = await SendToWebsocket.stream(
                    websocket=buffer.websocket,
                    chatroom_id=buffer.current_chatroom_id,
                    stream=generate_from_openai(
                        user_gpt_context=buffer.current_user_gpt_context
                    ),
                    finish=True,
                    model_name="chatgpt",
                )
            elif isinstance(
                buffer.current_user_gpt_context.gpt_model.value, LlamaCppModel
            ):
                m_queue, m_done = process_manager.Queue(), process_manager.Event()
                # async_queue, async_done = asyncio.Queue(), asyncio.Event()
                loop = asyncio.get_event_loop()
                prompt: str = message_history_organizer(
                    user_gpt_context=buffer.current_user_gpt_context,
                    return_as_string=True,
                )  # type: ignore
                try:
                    msg, _ = await asyncio.gather(
                        SendToWebsocket.stream(
                            websocket=buffer.websocket,
                            chatroom_id=buffer.current_chatroom_id,
                            finish=True,
                            chunk_size=1,
                            model_name="llama",
                            stream=generate_from_llama_cpp(
                                user_gpt_context=buffer.current_user_gpt_context,
                                m_queue=m_queue,
                                m_done=m_done,
                            ),
                        ),
                        loop.run_in_executor(
                            process_pool_executor,
                            llama_cpp_generation,
                            buffer.current_user_gpt_context.gpt_model.value,
                            prompt,
                            m_queue,
                            m_done,
                            buffer.current_user_gpt_context,
                        ),
                    )
                except Exception as e:
                    raise e
                finally:
                    m_done.set()

            else:
                raise GptModelNotImplementedException(
                    msg="Model not implemented. Please contact administrator."
                )
        except Exception:
            raise GptTextGenerationException(
                msg="An error occurred while generating text."
            )
