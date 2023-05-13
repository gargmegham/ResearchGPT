from dataclasses import dataclass, field

from gpt.common import UserGptContext


@dataclass
class BufferedUserContext:
    user_id: int
    sorted_contexts: list[UserGptContext]
    _current_context: UserGptContext = field(init=False)

    def __post_init__(self) -> None:
        self._current_context = self.sorted_contexts[0]

    def insert_context(self, user_gpt_context: UserGptContext, index: int = 0) -> None:
        self.sorted_contexts.insert(index, user_gpt_context)

    def delete_context(self, index: int) -> None:
        del self.sorted_contexts[index]

    def find_index_of_chatroom(self, chatroom_id: int) -> int | None:
        try:
            return self.sorted_chatroom_ids.index(chatroom_id)
        except ValueError:
            return None

    def change_context_to(self, index: int) -> None:
        self._current_context = self.sorted_contexts[index]

    @property
    def buffer_size(self) -> int:
        return len(self.sorted_contexts)

    @property
    def current_chatroom_id(self) -> str:
        return self.current_user_gpt_context.chatroom_id

    @property
    def sorted_user_gpt_contexts(self) -> list[UserGptContext]:
        return self.sorted_contexts

    @property
    def sorted_chatroom_ids(self) -> list[str]:
        return [context.chatroom_id for context in self.sorted_contexts]

    @property
    def current_user_gpt_context(self) -> UserGptContext:
        return self._current_context
