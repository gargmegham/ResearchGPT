from dataclasses import dataclass, field

from gpt.models import UserGptContext


@dataclass
class BufferedUserContext:
    user_id: str
    sorted_ctxts: list[UserGptContext]
    _current_ctxt: UserGptContext = field(init=False)

    def __post_init__(self) -> None:
        self._current_ctxt = self.sorted_ctxts[0]

    def insert_context(self, user_gpt_context: UserGptContext, index: int = 0) -> None:
        self.sorted_ctxts.insert(index, user_gpt_context)

    def delete_context(self, index: int) -> None:
        del self.sorted_ctxts[index]

    def find_index_of_chatroom(self, chatroom_id: str) -> int | None:
        try:
            return self.sorted_chatroom_ids.index(chatroom_id)
        except ValueError:
            return None

    def change_context_to(self, index: int) -> None:
        self._current_ctxt = self.sorted_ctxts[index]

    @property
    def buffer_size(self) -> int:
        return len(self.sorted_ctxts)

    @property
    def current_chatroom_id(self) -> str:
        return self.current_user_gpt_context.chatroom_id

    @property
    def sorted_user_gpt_contexts(self) -> list[UserGptContext]:
        return self.sorted_ctxts

    @property
    def sorted_chatroom_ids(self) -> list[str]:
        return [context.chatroom_id for context in self.sorted_ctxts]

    @property
    def current_user_gpt_context(self) -> UserGptContext:
        return self._current_ctxt
