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
from tiktoken import Encoding, get_encoding

MODEL_TO_ENCODING: dict[str, str] = {
    # text
    "text-davinci-003": "p50k_base",
    "text-davinci-002": "p50k_base",
    "text-davinci-001": "r50k_base",
    "text-curie-001": "r50k_base",
    "text-babbage-001": "r50k_base",
    "text-ada-001": "r50k_base",
    "davinci": "r50k_base",
    "curie": "r50k_base",
    "babbage": "r50k_base",
    "ada": "r50k_base",
    # code
    "code-davinci-002": "p50k_base",
    "code-davinci-001": "p50k_base",
    "code-cushman-002": "p50k_base",
    "code-cushman-001": "p50k_base",
    "davinci-codex": "p50k_base",
    "cushman-codex": "p50k_base",
    # edit
    "text-davinci-edit-001": "p50k_edit",
    "code-davinci-edit-001": "p50k_edit",
    # embeddings
    "text-embedding-ada-002": "cl100k_base",
    # old embeddings
    "text-similarity-davinci-001": "r50k_base",
    "text-similarity-curie-001": "r50k_base",
    "text-similarity-babbage-001": "r50k_base",
    "text-similarity-ada-001": "r50k_base",
    "text-search-davinci-doc-001": "r50k_base",
    "text-search-curie-doc-001": "r50k_base",
    "text-search-babbage-doc-001": "r50k_base",
    "text-search-ada-doc-001": "r50k_base",
    "code-search-babbage-code-001": "r50k_base",
    "code-search-ada-code-001": "r50k_base",
    # open source
    "gpt2": "gpt2",
    "gpt-4": "cl100k_base",
    "gpt-3.5-turbo": "cl100k_base",
    "gpt-35-turbo": "cl100k_base",  # making it compatible with Azure's naming restrictions
}


def encoding_for_model(model_name: str) -> Encoding:
    try:
        encoding_name = MODEL_TO_ENCODING[model_name]
    except KeyError:
        raise KeyError(
            f"Could not automatically map {model_name} to a tokeniser. "
            "Please use `tiktok.get_encoding` to explicitly get the tokeniser you expect."
        ) from None
    return get_encoding(encoding_name)


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
