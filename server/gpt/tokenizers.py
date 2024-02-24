"""
This module contains the tokenizer classes for the GPT-2 and GPT-Neo models.
A brief explanation of the tokenizer classes:
    - BaseTokenizer: The base class for all tokenizers. It is an abstract class
        that defines the interface for all tokenizers.
    - OpenAITokenizer: The tokenizer for the GPT-2 model. It uses the
        `transformers` library to tokenize the input.
    - LlamaTokenizer: The tokenizer for the GPT-Neo model. It uses the
        `transformers` library to tokenize the input.
Tokenization is the process of converting a string into a list of integers.
"""
from abc import ABC, abstractmethod

import transformers
from tiktoken.model import get_encoding


class BaseTokenizer(ABC):
    @abstractmethod
    def encode(self, message: str) -> list[int]:
        ...

    @abstractmethod
    def tokens_of(self, message: str) -> int:
        ...


class OpenAITokenizer(BaseTokenizer):
    def __init__(self):
        self._tokenizer = get_encoding("cl100k_base")

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
