from asyncio import gather
from enum import Enum
from functools import wraps
from inspect import Parameter, iscoroutinefunction, signature
from typing import Any, Callable, Tuple

from fastapi import WebSocket

from app.exceptions import ChatroomNotFound, InternalServerError
from gpt.buffer import BufferedUserContext
from gpt.cache_manager import ChatGptCacheManager
from gpt.common import GptRoles, LLMModels, UserGptContext
from gpt.message_handler import MessageHandler
from gpt.message_manager import MessageManager
from gpt.vectorstore_manager import Document, VectorStoreManager
from gpt.websocket_manager import SendToWebsocket


async def create_new_chatroom(
    user_id: int,
    new_chatroom_id: int,
) -> UserGptContext:
    default: UserGptContext = UserGptContext.construct_default(
        user_id=user_id,
        chatroom_id=new_chatroom_id,
    )
    await ChatGptCacheManager.create_context(user_gpt_context=default)
    return default


async def delete_old_chatroom(
    chatroom_id_to_delete: int,
    user_id: int,
) -> bool | None:
    await ChatGptCacheManager.delete_chatroom(
        user_id=user_id, chatroom_id=chatroom_id_to_delete
    )


async def get_contexts_sorted_from_recent_to_past(
    user_id: int, chatroom_ids: list[int]
) -> list[UserGptContext]:
    """
    Returns a list of contexts sorted from recent to past.
    :param user_id: user id
    :param chatroom_ids: list of chatroom ids
    """
    if len(chatroom_ids) == 0:
        raise ChatroomNotFound()
    else:
        # get latest chatroom
        contexts: list[UserGptContext] = await gather(
            *[
                ChatGptCacheManager.read_context(user_id=user_id, chatroom_id=id)
                for id in chatroom_ids
            ]
        )
        contexts.sort(key=lambda x: x.user_gpt_profile.created_at, reverse=True)
        return contexts


class ResponseType(str, Enum):
    """
    Enum to handle command responses
    """

    SEND_MESSAGE_AND_STOP = "send_message_and_stop"
    SEND_MESSAGE_AND_KEEP_GOING = "send_message_and_keep_going"
    HANDLE_USER = "handle_user"
    HANDLE_GPT = "handle_gpt"
    HANDLE_BOTH = "handle_both"
    DO_NOTHING = "do_nothing"
    REPEAT_COMMAND = "repeat_command"


class CommandResponse:
    """
    Class to handle command responses
    """

    @staticmethod
    def _wrapper(enum_type: ResponseType) -> Callable:
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Tuple[Any, ResponseType]:
                result = func(*args, **kwargs)
                return (result, enum_type)

            @wraps(func)
            async def async_wrapper(
                *args: Any, **kwargs: Any
            ) -> Tuple[Any, ResponseType]:
                result = await func(*args, **kwargs)
                return (result, enum_type)

            return async_wrapper if iscoroutinefunction(func) else sync_wrapper

        return decorator

    send_message_and_stop = _wrapper(ResponseType.SEND_MESSAGE_AND_STOP)
    send_message_and_keep_going = _wrapper(ResponseType.SEND_MESSAGE_AND_KEEP_GOING)
    handle_user = _wrapper(ResponseType.HANDLE_USER)
    handle_gpt = _wrapper(ResponseType.HANDLE_GPT)
    handle_both = _wrapper(ResponseType.HANDLE_BOTH)
    do_nothing = _wrapper(ResponseType.DO_NOTHING)
    repeat_command = _wrapper(ResponseType.REPEAT_COMMAND)


async def command_handler(
    callback_name: str,
    callback_args: list[str],
    buffer: BufferedUserContext,
):
    callback_response, response_type = await ChatGptCommands._get_command_response(
        callback_name=callback_name,
        callback_args=callback_args,
        buffer=buffer,
    )
    if response_type is ResponseType.DO_NOTHING:
        return
    elif response_type is ResponseType.HANDLE_GPT:
        await MessageHandler.gpt(
            buffer=buffer,
        )
        return
    elif response_type is ResponseType.HANDLE_USER:
        await MessageHandler.user(
            msg=callback_response,
            buffer=buffer,
        )
        return
    elif response_type is ResponseType.HANDLE_BOTH:
        await MessageHandler.user(
            msg=callback_response,
            buffer=buffer,
        )
        await MessageHandler.gpt(
            buffer=buffer,
        )
        return
    elif response_type is ResponseType.REPEAT_COMMAND:
        splitted: list[str] = callback_response.split(" ")
        await command_handler(
            callback_name=splitted[0][1:]
            if splitted[0].startswith("/")
            else splitted[0],
            callback_args=splitted[1:],
            buffer=buffer,
        )


def arguments_provider(
    func: Callable,
    available_args: list[Any],
    available_annotated: dict[Any, Any],
    available_kwargs: dict[str, Any],
) -> tuple[list[Any], dict[str, Any]]:
    args_to_pass: list[Any] = []
    kwargs_to_pass: dict[str, Any] = {}
    for param in signature(func).parameters.values():
        if param.kind == Parameter.VAR_POSITIONAL:
            args_to_pass.extend(available_args)
        elif param.kind == Parameter.VAR_KEYWORD:
            kwargs_to_pass.update(available_kwargs)
        elif param.kind == Parameter.KEYWORD_ONLY:
            if param.annotation in available_annotated:
                kwargs_to_pass[param.name] = available_annotated[param.annotation]
            else:
                raise InternalServerError()
        elif param.kind == Parameter.POSITIONAL_OR_KEYWORD:
            if param.annotation in available_annotated:
                kwargs_to_pass[param.name] = available_annotated[param.annotation]
            elif param.default is not Parameter.empty:
                kwargs_to_pass[param.name] = param.default
            else:
                try:
                    if param.annotation is Parameter.empty:
                        kwargs_to_pass[param.name] = available_args.pop(0)
                    else:
                        kwargs_to_pass[param.name] = param.annotation(
                            available_args.pop(0)
                        )
                except IndexError:
                    raise IndexError(
                        f"Required argument {param.name} is missing in available_args"
                    )
                except Exception:
                    raise TypeError(
                        f"Required argument {param.name} is missing in available_annotated"
                    )
        elif param.kind == Parameter.POSITIONAL_ONLY:
            if len(available_args) > 0:
                if param.annotation is str:
                    args_to_pass.append(" ".join(available_args))
                    available_args.clear()
                elif param.annotation is Parameter.empty:
                    args_to_pass.append(available_args.pop(0))
                else:
                    try:
                        args_to_pass.append(param.annotation(available_args.pop(0)))
                    except Exception:
                        raise TypeError(
                            f"Required argument {param.name} is missing in available_annotated"
                        )
            elif param.default is not Parameter.empty:
                args_to_pass.append(param.default)
            else:
                raise IndexError(
                    f"Required argument {param.name} is missing in available_args"
                )
    return args_to_pass, kwargs_to_pass


class ChatGptCommands:
    """
    Class for all commands that can be used in chat
    """

    @classmethod
    async def _get_command_response(
        cls,
        callback_name: str,
        callback_args: list[str],
        buffer: BufferedUserContext,
        **kwargs: Any,
    ) -> Tuple[Any, ResponseType]:
        if callback_name.startswith("_"):
            await SendToWebsocket.message(
                websocket=buffer.websocket,
                msg="Command name cannot start with '_'",
                chatroom_id=buffer.current_chatroom_id,
            )
            return None, ResponseType.DO_NOTHING
        else:
            callback: Callable = getattr(
                cls, callback_name, cls.not_existing_callback
            )  # get callback function
        try:
            args_to_pass, kwargs_to_pass = arguments_provider(
                func=callback,
                available_args=callback_args,
                available_annotated={
                    UserGptContext: buffer.current_user_gpt_context,
                    WebSocket: buffer.websocket,
                    BufferedUserContext: buffer,
                },
                available_kwargs=buffer.current_user_gpt_context.optional_info | kwargs,
            )
        except TypeError:
            await SendToWebsocket.message(
                websocket=buffer.websocket,
                msg="Wrong argument type",
                chatroom_id=buffer.current_chatroom_id,
            )
            return None, ResponseType.DO_NOTHING
        except IndexError:
            await SendToWebsocket.message(
                websocket=buffer.websocket,
                msg="Not enough arguments",
                chatroom_id=buffer.current_chatroom_id,
            )
            return None, ResponseType.DO_NOTHING
        else:
            if iscoroutinefunction(callback):  # if callback is coroutine function
                callback_response = await callback(*args_to_pass, **kwargs_to_pass)
            else:
                callback_response = callback(*args_to_pass, **kwargs_to_pass)
            if isinstance(callback_response, tuple):
                callback_response, response_type = callback_response
                if response_type in (
                    ResponseType.SEND_MESSAGE_AND_STOP,
                    ResponseType.SEND_MESSAGE_AND_KEEP_GOING,
                ):
                    await SendToWebsocket.message(
                        websocket=buffer.websocket,
                        msg=callback_response,
                        chatroom_id=buffer.current_chatroom_id,
                    )
                    return callback_response, (
                        ResponseType.HANDLE_BOTH
                        if response_type == ResponseType.SEND_MESSAGE_AND_KEEP_GOING
                        else ResponseType.DO_NOTHING
                    )
                return callback_response, response_type
            else:
                await SendToWebsocket.message(
                    websocket=buffer.websocket,
                    msg=callback_response,
                    chatroom_id=buffer.current_chatroom_id,
                )
                return None, ResponseType.DO_NOTHING

    @staticmethod
    @CommandResponse.send_message_and_stop
    def not_existing_callback() -> str:  # callback for not existing command
        return "Sorry, I don't know what you mean by..."

    @classmethod
    @CommandResponse.send_message_and_stop
    def help(cls) -> str:
        docs: list[str] = [
            getattr(cls, callback_name).__doc__
            for callback_name in dir(cls)
            if not callback_name.startswith("_")
        ]
        return "\n\n".join([doc for doc in docs if doc is not None])

    @staticmethod
    @CommandResponse.send_message_and_stop
    async def clear(
        user_gpt_context: UserGptContext,
    ) -> str:  # clear user and gpt message histories
        """Clear user and gpt message histories, and return the number of tokens removed\n
        /clear"""
        n_user_tokens: int = user_gpt_context.user_message_tokens
        n_gpt_tokens: int = user_gpt_context.gpt_message_tokens
        n_system_tokens: int = user_gpt_context.system_message_tokens
        for role in GptRoles:
            getattr(user_gpt_context, f"{role.name.lower()}_message_histories").clear()
            setattr(user_gpt_context, f"{role.name.lower()}_message_tokens", 0)
            await ChatGptCacheManager.delete_message_history(
                user_id=user_gpt_context.user_id,
                chatroom_id=user_gpt_context.chatroom_id,
                role=role,
            )
        response: str = f"""## Total Token Removed: **{n_user_tokens + n_gpt_tokens + n_system_tokens}**
- User: {n_user_tokens}
- GPT: {n_gpt_tokens}
- System: {n_system_tokens}"""
        return response  # return success message

    @staticmethod
    @CommandResponse.send_message_and_stop
    async def reset(user_gpt_context: UserGptContext) -> str:
        """
        Reset user_gpt_context\n
        """
        user_gpt_context.reset()
        if await ChatGptCacheManager.reset_context(
            user_id=user_gpt_context.user_id,
            chatroom_id=user_gpt_context.chatroom_id,
        ):
            return "Context reset success"
        else:
            return "Context reset failed"

    @staticmethod
    async def retry(
        user_gpt_context: UserGptContext,
    ) -> Tuple[str | None, ResponseType]:
        """Retry last message\n
        /retry"""
        if (
            len(user_gpt_context.user_message_histories) < 1
            or len(user_gpt_context.gpt_message_histories) < 1
        ):
            return "There is no message to retry.", ResponseType.SEND_MESSAGE_AND_STOP
        await MessageManager.pop_message_history_safely(
            user_gpt_context=user_gpt_context, role=GptRoles.GPT
        )
        return None, ResponseType.HANDLE_GPT

    @staticmethod
    @CommandResponse.send_message_and_stop
    async def codex(user_gpt_context: UserGptContext) -> str:
        """Let GPT act as CODEX("COding DEsign eXpert")\n
        /codex"""
        system_message = """Act as CODEX ("COding DEsign eXpert"), an expert coder with experience in multiple coding languages.
Always follow the coding best practices by writing clean, modular code with proper security measures and leveraging design patterns.
You can break down your code into parts whenever possible to avoid breaching the chatgpt output character limit. Write code part by part when I send "continue". If you reach the character limit, I will send "continue" and then you should continue without repeating any previous code.
Do not assume anything from your side; please ask me a numbered list of essential questions before starting.
If you have trouble fixing a bug, ask me for the latest code snippets for reference from the official documentation.
I am using [MacOS], [VSCode] and prefer [brew] package manager.
Start a conversation as "CODEX: Hi, what are we coding today?"
        """
        await MessageManager.clear_message_history_safely(
            user_gpt_context=user_gpt_context, role=GptRoles.SYSTEM
        )
        await MessageManager.add_message_history_safely(
            user_gpt_context=user_gpt_context,
            role=GptRoles.SYSTEM,
            content=system_message,
        )
        return "CODEX mode ON"

    @staticmethod
    @CommandResponse.send_message_and_stop
    async def redx(user_gpt_context: UserGptContext) -> str:
        """Let GPT reduce your message as much as possible\n
        /redx"""
        system_message = """compress the following text in a way that fits in a tweet (ideally) and such that you (GPT) can reconstruct the intention of the human who wrote text as close as possible to the original intention. This is for yourself. It does not need to be human readable or understandable. Abuse of language mixing, abbreviations, symbols (unicode and emoji), or any other encodings or internal representations is all permissible, as long as it, if pasted in a new inference cycle, will yield near-identical results as the original text: """
        await MessageManager.clear_message_history_safely(
            user_gpt_context=user_gpt_context, role=GptRoles.SYSTEM
        )
        await MessageManager.add_message_history_safely(
            user_gpt_context=user_gpt_context,
            role=GptRoles.SYSTEM,
            content=system_message,
        )
        return "REDX mode ON"

    @staticmethod
    @CommandResponse.send_message_and_stop
    def codeblock(language, codes: str, /) -> str:
        """Send codeblock\n
        /codeblock <language> <codes>"""
        return f"```{language.lower()}\n" + codes + "\n```"

    @staticmethod
    @CommandResponse.handle_gpt
    async def query(query: str, /, buffer: BufferedUserContext) -> None:
        """
        Query from redis vectorstore
        /query <query>
        """
        num_documents: int = 3
        found_document: list[Document] = (
            await VectorStoreManager.asimilarity_search(
                queries=[query], k=num_documents
            )
        )[0]
        found_text: str = "\n\n".join(
            [f"...{document.page_content}..." for document in found_document]
        )
        if len(found_document) > 0:
            query = f"""please answer my question\nquestion: `{query}`\nrelated context from my vectorstore:```{found_text}```\nanswer:"""
        await MessageManager.add_message_history_safely(
            user_gpt_context=buffer.current_user_gpt_context,
            content=query,
            role=GptRoles.USER,
        )

    @staticmethod
    @CommandResponse.send_message_and_stop
    async def embed(text_to_embed: str, /) -> str:
        """Embed the text and save its vectors in the redis vectorstore.\n
        /embed <text_to_embed>"""
        await VectorStoreManager.create_documents(
            text=text_to_embed,
        )
        return "Embedding successful!"

    @staticmethod
    @CommandResponse.send_message_and_stop
    def ping() -> str:
        """Ping! Pong!\n
        /ping"""
        return "pong"

    @staticmethod
    @CommandResponse.send_message_and_stop
    async def changemodel(model: str, user_chat_context: UserGptContext) -> str:
        """/changemodel <model>"""
        if model not in LLMModels._member_names_:
            return f"Model must be one of {', '.join(LLMModels._member_names_)}"
        llm_model: LLMModels = LLMModels._member_map_[model]  # type: ignore
        user_chat_context.llm_model = llm_model
        await ChatGptCacheManager.update_profile_and_model(user_chat_context)
        return f"Model changed to {model}. Actual model: {llm_model.value.name}"
