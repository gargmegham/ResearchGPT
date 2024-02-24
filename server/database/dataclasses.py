import logging
import re
from dataclasses import dataclass

from app.exceptions import APIException


@dataclass(frozen=True)
class ChatGPTConfig:
    # api url for openai
    api_url: str = "https://api.openai.com/v1/chat/completions"
    # wait for this time before timeout
    wait_for_timeout: float = 30.0
    # wait for this time before reconnecting
    wait_for_reconnect: float = 3.0
    api_regex_pattern: re.Pattern = re.compile(r"data:\s*({.+?})\n\n")
    # number of tokens to remove when tokens exceed token limit
    extra_token_margin: int = 100


@dataclass(frozen=True)
class Responses_500:
    """
    Responses 500
        - middleware_exception: Middleware exception
        - websocket_error: Websocket error
        - database_not_initialized: Database not initialized
        - cache_not_initialized: Cache not initialized
        - vectorestore_not_initialized: Vector Store not initialized
    """

    middleware_exception: APIException = APIException(
        status_code=500,
        internal_code=2,
        detail="Middleware could not be initialized",
    )
    websocket_error: APIException = APIException(
        status_code=500,
        internal_code=3,
        msg="Websocket error",
        detail="Websocket error",
    )
    database_not_initialized: APIException = APIException(
        status_code=500,
        internal_code=4,
        msg="Database not initialized",
        detail="Database not initialized",
    )
    cache_not_initialized: APIException = APIException(
        status_code=500,
        internal_code=5,
        msg="Cache not initialized",
        detail="Cache not initialized",
    )
    vectorestore_not_initialized: APIException = APIException(
        status_code=500,
        detail="Vector Store not initialized",
        msg="Vector Store not initialized",
        internal_code=5,
    )


@dataclass
class LoggingConfig:
    """
    Logging Config
        - logger_name: Logger name
        - logger_level: Logger level
        - console_log_level: Console log level
        - file_log_level: File log level
        - file_log_name: File log name
        - logging_format: Logging format
    """

    logger_level: int = logging.DEBUG
    console_log_level: int = logging.INFO
    file_log_level: int | None = logging.DEBUG
    file_log_name: str | None = "./log/app.log"
    logging_format: str = "[%(asctime)s] %(name)s:%(levelname)s - %(message)s"
