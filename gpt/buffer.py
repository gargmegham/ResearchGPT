from dataclasses import dataclass, field

from fastapi import WebSocket

from gpt.common import UserGptContext


@dataclass
class BufferedUserContext:
    """A buffered user context is a user context that is stored in memory"""

    user_id: int
    websocket: WebSocket | None
    sorted_contexts: list[UserGptContext]
    _current_context: UserGptContext = field(init=False)

    def __post_init__(self) -> None:
        self._current_context = self.sorted_contexts[0]

    def insert_context(self, user_gpt_context: UserGptContext, index: int = 0) -> None:
        self.sorted_contexts.insert(index, user_gpt_context)

    def delete_context(self, index: int) -> None:
        del self.sorted_contexts[index]

    def find_index_of_chatroom(self, chatroom_id: int) -> int | None:
        """find index of chatroom in sorted_chatroom_ids"""
        try:
            return self.sorted_chatroom_ids.index(chatroom_id)
        except ValueError:
            return None

    def change_context_to(self, index: int) -> None:
        self._current_context = self.sorted_contexts[index]

    @property
    def buffer_size(self) -> int:
        """Return the number of chatrooms in the buffer"""
        return len(self.sorted_contexts)

    @property
    def current_chatroom_id(self) -> str:
        return self.current_user_gpt_context.chatroom_id

    @property
    def sorted_user_gpt_contexts(self) -> list[UserGptContext]:
        return self.sorted_contexts

    @property
    def sorted_chatroom_ids(self) -> list[str]:
        """Return a list of chatroom ids in the order they were created"""
        return [context.chatroom_id for context in self.sorted_contexts]

    @property
    def current_user_gpt_context(self) -> UserGptContext:
        """Return the current user gpt context"""
        return self._current_context
