from configparser import RawConfigParser
from pathlib import Path

from app.config import Args

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
HOST_MAIN = config.get("main", "HOST_MAIN")
DEBUG_MODE = config.get("main", "DEBUG_MODE")

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
RESEARCHGPT_WAKING_PATTERN = Args.RESEARCHGPT_WAKING_PATTERN
RESEARCHGPT_TEXT_COLOR = Args.RESEARCHGPT_TEXT_COLOR
if DEBUG_MODE.lower() in ["1", "true"]:
    RESEARCHGPT_DEBUG_MODE = True
else:
    RESEARCHGPT_DEBUG_MODE: bool = False


"""
Redis variables
"""
REDIS_HOST = config.get("redis", "REDIS_HOST")
REDIS_PORT = config.get("redis", "REDIS_PORT")
REDIS_DB = config.get("redis", "REDIS_DB")
REDIS_USER = config.get("redis", "REDIS_USER")
REDIS_PASSWORD = config.get("redis", "REDIS_PASSWORD")


"""
Trusted host variables for TrustedHostMiddleware
Allowed sites variables for CORSMiddleware
"""
if DEBUG_MODE.lower() in ["1", "true"]:
    TRUSTED: list[str] = ["*"]
    ALLOWED: list[str] = ["*"]
else:
    TRUSTED: list[str] = [
        f"*.{HOST_MAIN}",
        HOST_MAIN,
        "localhost",
    ]
    ALLOWED: list[str] = [
        f"*.{HOST_MAIN}",
        HOST_MAIN,
        "localhost",
    ]
