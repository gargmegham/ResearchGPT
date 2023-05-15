import re


class Args:
    """
    path variables
    """

    LOG_DIR: str = "./log"
    PROMPTS_DIR: str = "./prompts"

    """
    ResearchGPT variables
    """
    DEBUG_KEY: str = "RESEARCHGPT_CHATROOM_SERVER_DEBUG"
    RESEARCHGPT_WAKING_PATTERN = re.compile(r"@researchgpt", re.IGNORECASE)
    RESEARCHGPT_TEXT_COLOR = "#DE3163"

    """
    other variables
    """
    PING_HOST = "www.google.com"

    """
    server message variables
    """
    UNKNOWN_RUNTIME_ERR_MSG = "【unknown system error, contact admin】"
    UNKNOWN_NETWORK_ERR_MSG = "【unknown network error, please try again】"
    ENTER_ROOM_MSG = "joined    online"
    EXIT_ROOM_MSG = "exited    online"
    EMPTY_INPUT_MSG = "【your message was empty】"
