from database.mysql import SQLAlchemy
from database.redis import RedisFactory

"""
MySQL Database
"""
db: SQLAlchemy = SQLAlchemy()


"""
Redis Cache
"""
cache: RedisFactory = RedisFactory()
