from os import environ
from pathlib import Path

from dotenv import load_dotenv

"""
SECRETS
"""
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "config/.env"
load_dotenv(dotenv_path=CONFIG_FILE)


"""
Main Secret Key
"""
HOST_MAIN: str = environ.get("HOST_MAIN")
DEBUG_MODE: str = environ.get("DEBUG_MODE")
SECRET_KEY: str = environ.get("SECRET_KEY")
DEFAULT_JWT_SECRET = environ.get("DEFAULT_JWT_SECRET")

"""
OpenAI API SECRETS
"""
OPENAI_API_KEY: str = environ.get("OPENAI_API_KEY")
DEFAULT_LLM_MODEL: str = environ.get("DEFAULT_LLM_MODEL")

"""
MySQL DB SECRETS
"""
MYSQL_HOST: str = environ.get("MYSQL_HOST")
MYSQL_USER: str = environ.get("MYSQL_USER")
MYSQL_PASSWORD: str = environ.get("MYSQL_PASSWORD")
MYSQL_PORT: str = environ.get("MYSQL_PORT")
MYSQL_DATABASE: str = environ.get("MYSQL_DATABASE")


"""
path variables
"""
LOG_DIR: str = "./log"


"""
Redis variables
"""
REDIS_HOST: str = environ.get("REDIS_HOST")
REDIS_PORT: str = environ.get("REDIS_PORT")
REDIS_DB: str = environ.get("REDIS_DB")
REDIS_USER: str = environ.get("REDIS_USER")
REDIS_PASSWORD: str = environ.get("REDIS_PASSWORD")

"""
PUBMED
"""
PUBMED_API_ENDPOINT: str = environ.get("PUBMED_API_ENDPOINT")
PUBMED_API_AUTH_HEADER: str = environ.get("PUBMED_API_AUTH_HEADER")

"""
Trusted host variables for TrustedHostMiddleware
Allowed sites variables for CORSMiddleware
"""
if DEBUG_MODE.lower() in ["1", "true"]:
    ALLOWED: list[str] = ["*"]
else:
    ALLOWED: list[str] = [
        HOST_MAIN,
        "localhost",
    ]
