import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ChatGPTConfig:
    api_url: str = "https://api.openai.com/v1/chat/completions"  # api url for openai
    wait_for_timeout: float = 30.0  # wait for this time before timeout
    wait_for_reconnect: float = 3.0  # wait for this time before reconnecting
    api_regex_pattern: re.Pattern = re.compile(r"data:\s*({.+?})\n\n")
    extra_token_margin: int = (
        100  # number of tokens to remove when tokens exceed token limit
    )
