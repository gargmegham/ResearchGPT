from orjson import dumps as orjson_dumps
from orjson import loads as orjson_loads
from sqlalchemy.exc import OperationalError
from sqlalchemy.future import select

from app.exceptions import MySQLConnectionError
from database import cache, db, models
from gpt.common import (
    GptRoles,
    LLMModels,
    MessageHistory,
    UserGptContext,
    UserGptProfile,
)


class ChatGptCacheManager:
    _string_fields: tuple = (
        "user_gpt_profile",
        "gpt_model",
    )
    _list_fields: tuple[str] = tuple(
        f"{role.name.lower()}_message_histories" for role in GptRoles
    )

    @staticmethod
    def _generate_key(user_id: int, chatroom_id: int, field: str) -> str:
        return f"chatgpt:{user_id}:{chatroom_id}:{field}"

    @classmethod
    def _get_string_fields(cls, user_id: int, chatroom_id: int) -> dict[str, str]:
        return {
            field: cls._generate_key(user_id, chatroom_id, field)
            for field in cls._string_fields
        }

    @classmethod
    def _get_list_fields(cls, user_id: int, chatroom_id: int) -> dict[str, str]:
        return {
            field: cls._generate_key(user_id, chatroom_id, field)
            for field in cls._list_fields
        }

    @classmethod
    async def get_all_chatrooms(cls, user_id: int) -> list[int]:
        """
        Get all chatrooms
        :param user_id: user id
        :return: list of chatroom ids
        """
        chatroom_ids: list[int] = []
        try:
            async with db.session() as transaction:
                q = select(models.Chatroom).where(models.Chatroom.user_id == user_id)
                result = await transaction.execute(q)
                chatroom_ids = [chatroom.id for chatroom in result.scalars().all()]
            return chatroom_ids
        except OperationalError:
            raise MySQLConnectionError(
                "MySQL connection error. Please try again later."
            )

    @classmethod
    async def read_context(cls, user_id: int, chatroom_id: int) -> UserGptContext:
        stored_string: dict[str, str | None] = {
            field: await cache.redis.get(key)
            for field, key in cls._get_string_fields(user_id, chatroom_id).items()
        }
        stored_list: dict[str, list | None] = {
            field: await cache.redis.lrange(key, 0, -1)
            for field, key in cls._get_list_fields(user_id, chatroom_id).items()
        }

        # if any of stored strings are None, create new context
        if any([value is None for value in stored_string.values()]):
            default: UserGptContext = UserGptContext.construct_default(
                user_id=user_id,
                chatroom_id=chatroom_id,
            )
            await cls.create_context(default)
            return default

        for field, value in stored_string.items():
            if value is not None:
                stored_string[field] = orjson_loads(value)
        for field, value in stored_list.items():
            if value is not None:
                stored_list[field] = [orjson_loads(v) for v in value]

        return UserGptContext(
            user_gpt_profile=UserGptProfile(**stored_string["user_gpt_profile"]),  # type: ignore
            gpt_model=LLMModels._member_map_[stored_string["gpt_model"]],  # type: ignore
            user_message_histories=[
                MessageHistory(**m) for m in stored_list["user_message_histories"]
            ]
            if stored_list["user_message_histories"] is not None
            else [],
            gpt_message_histories=[
                MessageHistory(**m) for m in stored_list["gpt_message_histories"]
            ]
            if stored_list["gpt_message_histories"] is not None
            else [],
            system_message_histories=[
                MessageHistory(**m) for m in stored_list["system_message_histories"]
            ]
            if stored_list["system_message_histories"] is not None
            else [],
        )

    @classmethod
    async def create_context(
        cls,
        user_gpt_context: UserGptContext,
        only_if_exists: bool = False,
        only_if_not_exists: bool = True,
    ) -> bool:
        json_data = user_gpt_context.json()
        success: bool = True
        for field, key in cls._get_string_fields(
            user_gpt_context.user_id, user_gpt_context.chatroom_id
        ).items():
            result = await cache.redis.set(
                key,
                orjson_dumps(json_data[field]),
                xx=only_if_exists,
                nx=only_if_not_exists,
            )
            success &= bool(result)
        for field, key in cls._get_list_fields(
            user_gpt_context.user_id, user_gpt_context.chatroom_id
        ).items():
            result = await cache.redis.delete(key)
            for item in json_data[field]:
                result = await cache.redis.rpush(key, orjson_dumps(item))
                success &= bool(result)

        return success

    @classmethod
    async def reset_context(
        cls,
        user_id: int,
        chatroom_id: int,
        only_if_exists: bool = True,
        only_if_not_exists: bool = False,
    ) -> bool:
        return await cls.create_context(
            UserGptContext.construct_default(
                user_id=user_id,
                chatroom_id=chatroom_id,
            ),
            only_if_exists=only_if_exists,
            only_if_not_exists=only_if_not_exists,
        )

    @classmethod
    async def update_context(
        cls,
        user_gpt_context: UserGptContext,
        only_if_exists: bool = True,
    ) -> bool:
        json_data = user_gpt_context.json()
        success = True
        for field, key in cls._get_string_fields(
            user_gpt_context.user_id,
            user_gpt_context.chatroom_id,
        ).items():
            result = await cache.redis.set(
                key,
                orjson_dumps(json_data[field]),
                xx=only_if_exists,
            )
            success &= bool(result)
        for field, key in cls._get_list_fields(
            user_gpt_context.user_id,
            user_gpt_context.chatroom_id,
        ).items():
            result = await cache.redis.delete(key)
            success &= bool(result)
            for item in json_data[field]:
                result = await cache.redis.rpush(key, orjson_dumps(item))
                success &= bool(result)
        return success

    @classmethod
    async def delete_chatroom(cls, user_id: int, chatroom_id: int) -> int:
        """
        Delete all keys starting with "chatgpt:{user_id}:{chatroom_id}:
        """
        keys = [
            key
            async for key in cache.redis.scan_iter(f"chatgpt:{user_id}:{chatroom_id}:*")
        ]
        if not keys:
            return 0
        return await cache.redis.delete(*keys)

    @classmethod
    async def update_profile_and_model(
        cls,
        user_gpt_context: UserGptContext,
        only_if_exists: bool = True,
    ) -> bool:
        json_data = user_gpt_context.json()
        success = True

        for field, key in cls._get_string_fields(
            user_gpt_context.user_id,
            user_gpt_context.chatroom_id,
        ).items():
            result = await cache.redis.set(
                key,
                orjson_dumps(json_data[field]),
                xx=only_if_exists,
            )
            success &= bool(result)
        return success

    @classmethod
    async def update_message_histories(
        cls,
        user_id: int,
        chatroom_id: int,
        role: GptRoles | str,
        message_histories: list[MessageHistory],
    ) -> bool:
        role = GptRoles.get_name(role).lower()
        key = cls._generate_key(user_id, chatroom_id, f"{role}_message_histories")
        message_histories_json = [
            orjson_dumps(message_history.__dict__)
            for message_history in message_histories
        ]
        result = await cache.redis.delete(key)
        result &= await cache.redis.rpush(key, *message_histories_json)
        return bool(result)

    @classmethod
    async def lpop_message_history(
        cls,
        user_id: int,
        chatroom_id: int,
        role: GptRoles | str,
        count: int | None = None,
    ) -> MessageHistory | list[MessageHistory] | None:
        role = GptRoles.get_name(role).lower()
        assert count is None or count > 0
        message_history_json: str | list | None = await cache.redis.lpop(
            cls._generate_key(user_id, chatroom_id, f"{role}_message_histories"),
            count=count,
        )
        if message_history_json is None:
            return None
        # if message_history_json is instance of list, then it is a list of message histories
        if isinstance(message_history_json, list):
            return [MessageHistory(**orjson_loads(m)) for m in message_history_json]
        # otherwise, it is a single message history
        return MessageHistory(**orjson_loads(message_history_json))

    @classmethod
    async def rpop_message_history(
        cls,
        user_id: int,
        chatroom_id: int,
        role: GptRoles | str,
        count: int | None = None,
    ) -> MessageHistory | list[MessageHistory] | None:
        role = GptRoles.get_name(role).lower()
        assert count is None or count > 0
        message_history_json = await cache.redis.rpop(
            cls._generate_key(user_id, chatroom_id, f"{role}_message_histories"),
            count=count,
        )
        if message_history_json is None:
            return None
        # if message_history_json is instance of list, then it is a list of message histories
        if isinstance(message_history_json, list):
            return [MessageHistory(**orjson_loads(m)) for m in message_history_json]
        # otherwise, it is a single message history
        return MessageHistory(**orjson_loads(message_history_json))

    @classmethod
    async def append_message_history(
        cls,
        user_id: int,
        chatroom_id: int,
        role: GptRoles | str,
        message_history: MessageHistory,
        if_exists: bool = False,
    ) -> bool:
        role = GptRoles.get_name(role).lower()
        message_history_key = cls._generate_key(
            user_id, chatroom_id, f"{role}_message_histories"
        )
        message_history_json = orjson_dumps(message_history.__dict__)
        result = (
            await cache.redis.rpush(message_history_key, message_history_json)
            if not if_exists
            else await cache.redis.rpushx(message_history_key, message_history_json)
        )
        return bool(result)

    @classmethod
    async def get_message_history(
        cls,
        user_id: int,
        chatroom_id: int,
        role: GptRoles | str,
    ) -> list[MessageHistory]:
        role = GptRoles.get_name(role).lower()
        key = cls._generate_key(user_id, chatroom_id, f"{role}_message_histories")
        raw_message_histories = await cache.redis.lrange(key, 0, -1)
        if raw_message_histories is None:
            return []
        return [
            MessageHistory(**orjson_loads(raw_message_history))
            for raw_message_history in raw_message_histories
        ]

    @classmethod
    async def delete_message_history(
        cls,
        user_id: int,
        chatroom_id: int,
        role: GptRoles | str,
    ) -> bool:
        role = GptRoles.get_name(role).lower()
        key = cls._generate_key(user_id, chatroom_id, f"{role}_message_histories")
        result = await cache.redis.delete(key)
        return bool(result)

    @classmethod
    async def set_message_history(
        cls,
        user_id: int,
        chatroom_id: int,
        message_history: MessageHistory,
        index: int,
        role: GptRoles | str,
    ) -> bool:
        """
        Set the message history at the given index to the given message history
        """
        role = GptRoles.get_name(role).lower()
        key = cls._generate_key(user_id, chatroom_id, f"{role}_message_histories")
        # value in redis is a list of message histories
        # set the last element of the list to the new message history
        result = await cache.redis.lset(
            key, index, orjson_dumps(message_history.__dict__)
        )
        return bool(result)
