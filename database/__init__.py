from database.mysql import SQLAlchemy
from database.redis import RedisFactory

db: SQLAlchemy = SQLAlchemy()

cache: RedisFactory = RedisFactory()
