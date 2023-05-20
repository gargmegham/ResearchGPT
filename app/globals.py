from configparser import RawConfigParser
from pathlib import Path

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
HOST_MAIN: str = config.get("main", "HOST_MAIN")
DEBUG_MODE: str = config.get("main", "DEBUG_MODE")
SECRET_KEY: str = config.get("main", "SECRET_KEY")

"""
OpenAI API SECRETS
"""
OPENAI_API_KEY: str = config.get("openai", "OPENAI_API_KEY")
DEFAULT_LLM_MODEL: str = config.get("openai", "DEFAULT_LLM_MODEL")

"""
MySQL DB SECRETS
"""
MYSQL_HOST: str = config.get("mysql", "MYSQL_HOST")
MYSQL_USER: str = config.get("mysql", "MYSQL_USER")
MYSQL_PASSWORD: str = config.get("mysql", "MYSQL_PASSWORD")
MYSQL_PORT: str = config.get("mysql", "MYSQL_PORT")
MYSQL_DATABASE: str = config.get("mysql", "MYSQL_DATABASE")


"""
path variables
"""
LOG_DIR: str = "./log"


"""
Redis variables
"""
REDIS_HOST: str = config.get("redis", "REDIS_HOST")
REDIS_PORT: str = config.get("redis", "REDIS_PORT")
REDIS_DB: str = config.get("redis", "REDIS_DB")
REDIS_USER: str = config.get("redis", "REDIS_USER")
REDIS_PASSWORD: str = config.get("redis", "REDIS_PASSWORD")


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
