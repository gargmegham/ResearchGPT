from abc import ABC, abstractmethod

import transformers
from tiktoken import encoding_for_model


class BaseTokenizer(ABC):
    @abstractmethod
    def encode(self, message: str) -> list[int]:
        ...

    @abstractmethod
    def tokens_of(self, message: str) -> int:
        ...


class OpenAITokenizer(BaseTokenizer):
    def __init__(self, model_name: str):
        self._tokenizer = encoding_for_model(model_name)

    def encode(self, message: str, /) -> list[int]:
        return self._tokenizer.encode(message)

    def tokens_of(self, message: str) -> int:
        return len(self.encode(message))


class LlamaTokenizer(BaseTokenizer):
    def __init__(self, model_name: str):
        self._tokenizer = transformers.LlamaTokenizer.from_pretrained(model_name)

    def encode(self, message: str, /) -> list[int]:
        return self._tokenizer.encode(message)

    def tokens_of(self, message: str) -> int:
        return len(self.encode(message))
