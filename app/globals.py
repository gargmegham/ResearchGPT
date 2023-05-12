import logging
import os
from configparser import RawConfigParser
from pathlib import Path
from typing import Dict, List, Union

from config.en import Args

logger = logging.getLogger(__name__)

"""
OpenAI API SECRETS
"""
config = RawConfigParser()
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config/config.ini"
config.read(CONFIG_FILE)

"""
Main Secret Key
"""
SECRET_KEY = config.get("main", "SECRET_KEY")

"""
OpenAI API SECRETS
"""
OPENAI_API_KEY = config.get("openai", "OPENAI_API_KEY")
OPENAI_ORG_ID = config.get("openai", "OPENAI_ORG_ID")

"""
MySQL DB SECRETS
"""
MYSQL_HOST = config.get("mysql", "MYSQL_HOST")
MYSQL_USER = config.get("mysql", "MYSQL_USER")
MYSQL_PASSWORD = config.get("mysql", "MYSQL_PASSWORD")
MYSQL_PORT = config.get("mysql", "MYSQL_PORT")
MYSQL_DATABASE = config.get("mysql", "MYSQL_DATABASE")


"""
path variables
"""
LOG_DIR: str = Args.LOG_DIR
PROMPTS_DIR: str = Args.PROMPTS_DIR


"""
ResearchGPT variables
"""
DEBUG_KEY: str = Args.DEBUG_KEY
RESEARCHGPT_WAKING_PATTERN = Args.RESEARCHGPT_WAKING_PATTERN
RESEARCHGPT_TEXT_COLOR = Args.RESEARCHGPT_TEXT_COLOR
if DEBUG_KEY in os.environ and str(os.environ[DEBUG_KEY]).lower() in ["1", "true"]:
    RESEARCHGPT_DEBUG_MODE = True
else:
    RESEARCHGPT_DEBUG_MODE: bool = False


"""
other variables
"""
PING_HOST = Args.PING_HOST


"""
server message variables
"""
UNKNOWN_RUNTIME_ERR_MSG = Args.UNKNOWN_RUNTIME_ERR_MSG
UNKNOWN_NETWORK_ERR_MSG = Args.UNKNOWN_NETWORK_ERR_MSG
ENTER_ROOM_MSG = Args.ENTER_ROOM_MSG
EXIT_ROOM_MSG = Args.EXIT_ROOM_MSG
EMPTY_INPUT_MSG = Args.EMPTY_INPUT_MSG


"""
fastapi app instance
"""
USER_CONTEXT_DICT: Dict[str, Union[None, List]] = {}
