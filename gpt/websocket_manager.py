from typing import AsyncGenerator, AsyncIterator, Generator, Iterator

from fastapi import WebSocket

from database.schemas import MessageToWebsocket
from gpt.buffer import BufferedUserContext
from pubtrawlr import pubmed_context


class SendToWebsocket:
    @staticmethod
    async def init(
        buffer: BufferedUserContext,
    ) -> None:
        await pubmed_context(buffer.current_chatroom_id)

    @staticmethod
    async def message(
        websocket: WebSocket,
        msg: str,
        chatroom_id: int,
        finish: bool = True,
        is_user: bool = False,
        init: bool = False,
        model_name: str | None = None,
    ) -> None:
        """Send whole message to websocket"""
        if websocket.client_state.value != 1:
            return
        await websocket.send_json(
            MessageToWebsocket(
                msg=msg,
                finish=finish,
                chatroom_id=chatroom_id,
                is_user=is_user,
                init=init,
                model_name=model_name,
            ).dict()
        )

    @staticmethod
    async def stream(
        buffer: BufferedUserContext,
        stream: AsyncGenerator | Generator | AsyncIterator | Iterator,
        finish: bool = True,
        is_user: bool = False,
        chunk_size: int = 2,
        model_name: str | None = None,
    ) -> str:
        """Send SSE stream to websocket"""
        final_response, stream_buffer = "", ""
        iteration: int = 0
        await buffer.websocket.send_json(
            MessageToWebsocket(
                msg=None,
                finish=False,
                chatroom_id=buffer.current_chatroom_id,
                is_user=is_user,
                model_name=model_name,
            ).dict()
        )
        try:
            if isinstance(stream, (Generator, Iterator)):
                for delta in stream:
                    # stream from local llama_cpp
                    if buffer.done.is_set():
                        buffer.done.clear()
                        raise InterruptedError("Stream was interrupted by user.")
                    stream_buffer += delta
                    iteration += 1
                    if iteration % chunk_size == 0:
                        final_response += stream_buffer
                        await buffer.websocket.send_json(
                            MessageToWebsocket(
                                msg=stream_buffer,
                                finish=False,
                                chatroom_id=buffer.current_chatroom_id,
                                is_user=is_user,
                            ).dict()
                        )
                        stream_buffer = ""
            elif isinstance(stream, (AsyncGenerator, AsyncIterator)):
                async for delta in stream:
                    # stream from api
                    if buffer.done.is_set():
                        buffer.done.clear()
                        raise InterruptedError("Stream was interrupted by user.")
                    stream_buffer += delta
                    iteration += 1
                    if iteration % chunk_size == 0:
                        final_response += stream_buffer
                        await buffer.websocket.send_json(
                            MessageToWebsocket(
                                msg=stream_buffer,
                                finish=False,
                                chatroom_id=buffer.current_chatroom_id,
                                is_user=is_user,
                            ).dict()
                        )
                        stream_buffer = ""
            else:
                raise TypeError("Stream type is not AsyncGenerator or Generator.")
        except InterruptedError as e:
            await buffer.websocket.send_json(
                MessageToWebsocket(
                    msg=stream_buffer,
                    finish=True,
                    chatroom_id=buffer.current_chatroom_id,
                    is_user=is_user,
                ).dict()
            )
            raise e
        await buffer.websocket.send_json(
            MessageToWebsocket(
                msg=stream_buffer,
                finish=True if finish else False,
                chatroom_id=buffer.current_chatroom_id,
                is_user=is_user,
            ).dict()
        )
        return final_response
