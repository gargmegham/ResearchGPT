import asyncio

from app.dependencies import process_manager, process_pool_executor
from app.exceptions import (
    GptInterruptedException,
    GptModelNotImplementedException,
    GptTextGenerationException,
    GptTooMuchTokenException,
)
from gpt.buffer import BufferedUserContext
from gpt.common import GptRoles, LlamaCppModel, LLMModel, OpenAIModel
from gpt.generation import (
    generate_from_llama_cpp,
    generate_from_openai,
    message_history_organizer,
)
from gpt.llama_cpp import llama_cpp_generation
from gpt.message_manager import MessageManager
from gpt.websocket_manager import SendToWebsocket


class MessageHandler:
    """
    Handle messages from websocket
        - user message
            * add to message history
        - gpt message
            * generate text
            * send to websocket
    """

    @staticmethod
    async def user(
        msg: str,
        buffer: BufferedUserContext,
    ) -> None:
        """Handle user message"""
        user_token: int = buffer.current_user_gpt_context.get_tokens_of(msg)
        if user_token > buffer.current_user_gpt_context.token_per_request:
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
        """Handle gpt message, including text generation"""
        current_model: LLMModel = buffer.current_user_gpt_context.gpt_model.value
        try:
            if isinstance(current_model, OpenAIModel):
                await SendToWebsocket.stream(
                    buffer=buffer,
                    stream=generate_from_openai(
                        user_gpt_context=buffer.current_user_gpt_context
                    ),
                    finish=True,
                    model_name=current_model.name,
                )
            elif isinstance(
                buffer.current_user_gpt_context.gpt_model.value, LlamaCppModel
            ):
                m_queue, m_done = process_manager.Queue(), process_manager.Event()
                loop = asyncio.get_event_loop()
                prompt: str = message_history_organizer(
                    user_gpt_context=buffer.current_user_gpt_context,
                    return_as_string=True,
                )
                try:
                    await asyncio.gather(
                        SendToWebsocket.stream(
                            buffer=buffer,
                            finish=True,
                            chunk_size=1,
                            model_name=current_model.name,
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
        except InterruptedError as e:
            raise GptInterruptedException(msg=str(e))
        except Exception:
            raise GptTextGenerationException(
                msg="An error occurred while generating text."
            )
