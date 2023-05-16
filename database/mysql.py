from asyncio import current_task
from collections.abc import Iterable
from typing import Any, AsyncGenerator, Callable, Optional, Type
from urllib import parse

from sqlalchemy import (
    Delete,
    Result,
    ScalarResult,
    Select,
    TextClause,
    Update,
    create_engine,
    text,
)
from sqlalchemy.engine.base import Connection, Engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy_utils import create_database, database_exists

from app.globals import (
    MYSQL_DATABASE,
    MYSQL_HOST,
    MYSQL_PASSWORD,
    MYSQL_PORT,
    MYSQL_USER,
)
from app.logger import CustomLogger, logging_config
from database.dataclasses import Responses_500
from database.models import Base
from database.utils import SingletonMetaClass


class MySQL(metaclass=SingletonMetaClass):
    """
    MySQL: MySQL database class
        - engine: SQLAlchemy engine
        - session: SQLAlchemy session
        - async_engine: SQLAlchemy async engine
        - async_session: SQLAlchemy async session
        - logger: Custom logger
    """

    query_set: dict = {
        "is_user_exists": "SELECT EXISTS(SELECT 1 FROM mysql.user WHERE user = '{user}');",
        "is_db_exists": "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '{database}';",
        "is_user_granted": (
            "SELECT * FROM information_schema.schema_privileges "
            "WHERE table_schema = '{database}' AND grantee = '{user}';"
        ),
        "create_user": "CREATE USER '{user}'@'{host}' IDENTIFIED BY '{password}'",
        "grant_user": "GRANT {grant} ON {on} TO '{to_user}'@'{user_host}'",
        "create_db": "CREATE DATABASE {database} CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;",
        "drop_db": "DROP DATABASE {database};",
    }

    @staticmethod
    def execute(
        query: str, engine_or_conn: Engine | Connection, scalar: bool = False
    ) -> Any | None:
        """
        Execute query
            - query: Query
            - engine_or_conn: Engine or connection
            - scalar: scalar or not, which means return single value or not
        """
        if isinstance(engine_or_conn, Engine) and not isinstance(
            engine_or_conn, Connection
        ):
            with engine_or_conn.connect() as conn:
                cursor = conn.execute(
                    text(query + ";" if not query.endswith(";") else query)
                )
                return cursor.scalar() if scalar else None
        elif isinstance(engine_or_conn, Connection):
            cursor = engine_or_conn.execute(
                text(query + ";" if not query.endswith(";") else query)
            )
            return cursor.scalar() if scalar else None

    @staticmethod
    def clear_all_table_data(engine: Engine, except_tables: list[str] | None = None):
        """
        Clear all table data
            - engine: Engine
            - except_tables: Except tables
        """

        with engine.connect() as conn:
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
            for table in Base.metadata.sorted_tables:
                if except_tables is not None:
                    conn.execute(
                        table.delete()
                    ) if table.name not in except_tables else ...
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
            conn.commit()

    @classmethod
    def is_db_exists(cls, database: str, engine_or_conn: Engine | Connection) -> bool:
        """
        Check database exists or not
            - database: Database
            - engine_or_conn: Engine or connection
        """
        return bool(
            cls.execute(
                cls.query_set["is_db_exists"].format(database=database),
                engine_or_conn,
                scalar=True,
            )
        )

    @classmethod
    def is_user_exists(cls, user: str, engine_or_conn: Engine | Connection) -> bool:
        """
        Check user exists or not
            - user: User
            - engine_or_conn: Engine or connection
        """
        return bool(
            cls.execute(
                cls.query_set["is_user_exists"].format(user=user),
                engine_or_conn,
                scalar=True,
            )
        )

    @classmethod
    def is_user_granted(
        cls, user: str, database: str, engine_or_conn: Engine | Connection
    ) -> bool:
        """
        Check if user is granted
            - user: User
            - database: Database
            - engine_or_conn: Engine or connection
        """
        return bool(
            cls.execute(
                cls.query_set["is_user_granted"].format(user=user, database=database),
                engine_or_conn,
                scalar=True,
            )
        )

    @classmethod
    def drop_db(cls, database: str, engine_or_conn: Engine | Connection) -> None:
        """
        Drop database
        """
        return cls.execute(
            cls.query_set["drop_db"].format(database=database),
            engine_or_conn,
        )

    @classmethod
    def create_db(cls, database: str, engine_or_conn: Engine | Connection) -> None:
        """
        Create database
        """
        return cls.execute(
            cls.query_set["create_db"].format(database=database),
            engine_or_conn,
        )

    @classmethod
    def create_user(
        cls,
        user: str,
        password: str,
        host: str,
        engine_or_conn: Engine | Connection,
    ) -> None:
        """
        Create user
        """
        return cls.execute(
            cls.query_set["create_user"].format(
                user=user, password=password, host=host
            ),
            engine_or_conn,
        )

    @classmethod
    def grant_user(
        cls,
        grant: str,
        on: str,
        to_user: str,
        user_host: str,
        engine_or_conn: Engine | Connection,
    ) -> None:
        """
        Grant user
        """
        return cls.execute(
            cls.query_set["grant_user"].format(
                grant=grant, on=on, to_user=to_user, user_host=user_host
            ),
            engine_or_conn,
        )


class SQLAlchemy(metaclass=SingletonMetaClass):
    def __init__(self):
        self.root_engine: Engine | None = None
        self.engine: AsyncEngine | None = None
        self.session: async_scoped_session[AsyncSession] | None = None
        self.is_initiated = False
        self.logger = CustomLogger("SQLAlchemy", logging_config=logging_config)

    def start(self) -> None:
        """
        Start
            - create root engine
            - create database
            - create user
            - grant user
            - create engine
            - create session
            - set is_initiated to True
        """
        if self.is_initiated:
            return
        self.root_operations()
        database_url = "{dialect}+{driver}://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4".format(
            dialect="mysql",
            driver="aiomysql",
            user=MYSQL_USER,
            password=parse.quote(MYSQL_PASSWORD),
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            database=MYSQL_DATABASE,
        )
        self.engine = create_async_engine(
            database_url,
            echo=False,
            pool_recycle=900,
            pool_pre_ping=True,
        )
        self.session = async_scoped_session(
            async_sessionmaker(
                bind=self.engine, autocommit=False, autoflush=False, future=True
            ),
            scopefunc=current_task,
        )
        self.is_initiated = True

    def root_operations(self) -> None:
        """
        Root operations
            - Create database
            - Create user
            - Grant user
        """
        try:
            root_url = "{dialect}+{driver}://{user}:{password}@{host}:{port}/{database}?charset=utf8mb4".format(
                dialect="mysql",
                driver="pymysql",
                user="root",
                password=parse.quote(MYSQL_PASSWORD),
                host=MYSQL_HOST,
                port=MYSQL_PORT,
                database=MYSQL_DATABASE,
            )
            if not database_exists(root_url):
                create_database(root_url)
            self.root_engine = create_engine(root_url, echo=False)
            with self.root_engine.connect() as conn:
                if not MySQL.is_user_exists(MYSQL_USER, engine_or_conn=conn):
                    MySQL.create_user(
                        MYSQL_USER, MYSQL_PASSWORD, "%", engine_or_conn=conn
                    )
                if not MySQL.is_user_granted(
                    MYSQL_USER, MYSQL_DATABASE, engine_or_conn=conn
                ):
                    MySQL.grant_user(
                        "ALL PRIVILEGES",
                        f"{MYSQL_DATABASE}.*",
                        MYSQL_USER,
                        "%",
                        engine_or_conn=conn,
                    )
                Base.metadata.create_all(conn)
                conn.commit()
        except:
            pass
        finally:
            if self.root_engine is not None:
                self.root_engine.dispose()

    async def close(self) -> None:
        """
        Close
            - close session
            - dispose engine
            - set is_initiated to False
        """
        if self.session is None or self.engine is None:
            return
        await self.session.close()
        await self.engine.dispose()
        self.is_initiated = False

    async def get_db(self) -> AsyncGenerator[AsyncSession, str]:
        """
        Get db
            - if session is None, raise database_not_initialized
            - else, yield session
        """
        if self.session is None:
            raise Responses_500.database_not_initialized
        async with self.session() as transaction:
            yield transaction

    def run_in_session(self, func: Callable) -> Callable:
        """
        Run in session
            - if session is None, raise database_not_initialized
            - else, run func
        """

        async def wrapper(
            session: AsyncSession | None = None,
            autocommit: bool = False,
            refresh: bool = False,
            *args: Any,
            **kwargs: Any,
        ):
            if session is None:
                if self.session is None:
                    raise Responses_500.database_not_initialized
                async with self.session() as transaction:
                    result = await func(transaction, *args, **kwargs)
                    if autocommit:
                        await transaction.commit()
                    if refresh:
                        [await transaction.refresh(r) for r in result] if isinstance(
                            result, Iterable
                        ) else await transaction.refresh(result)
            else:
                result = await func(session, *args, **kwargs)
                if autocommit:
                    await session.commit()
                if refresh:
                    [await session.refresh(r) for r in result] if isinstance(
                        result, Iterable
                    ) else await session.refresh(result)
            return result

        return wrapper

    def log(self, msg) -> None:
        self.api_logger.critical(msg)

    # TODO: add decorator
    async def _execute(
        self, session: AsyncSession, stmt: TextClause | Update | Delete | Select
    ) -> Result:
        """
        Execute
            - execute stmt
        """
        return await session.execute(stmt)

    # TODO: add decorator
    async def _scalar(
        self,
        session: AsyncSession,
        stmt: Select,
    ) -> Any:
        """
        Scalar
            - execute stmt
        """
        return await session.scalar(stmt)

    # TODO: add decorator
    async def _scalars(
        self,
        session: AsyncSession,
        stmt: Select,
    ) -> ScalarResult:
        """
        Scalars
        """
        return await session.scalars(stmt)

    # TODO: add decorator
    async def _add(
        self,
        session: AsyncSession,
        instance: DeclarativeMeta,
    ) -> DeclarativeMeta:
        """
        Add
        """
        session.add(instance)
        return instance

    # TODO: add decorator
    async def _add_all(
        self,
        session: AsyncSession,
        instances: Iterable[DeclarativeMeta],
    ) -> Iterable[DeclarativeMeta]:
        """
        Add all
        """
        session.add_all(instances)
        return instances

    # TODO: add decorator
    async def _delete(
        self,
        session: AsyncSession,
        instance: DeclarativeMeta,
    ) -> DeclarativeMeta:
        """
        Delete
        """
        await session.delete(instance)
        return instance

    async def execute(
        self,
        stmt: TextClause | Update | Delete | Select,
        autocommit: bool = False,
        refresh: bool = False,
        session: AsyncSession | None = None,
    ) -> Result:
        """
        Execute: running in session with autocommit and refresh
            - execute stmt
        """
        return await self.run_in_session(self._execute)(
            session, autocommit=autocommit, refresh=refresh, stmt=stmt
        )

    async def scalar(self, stmt: Select, session: AsyncSession | None = None) -> Any:
        return await self.run_in_session(self._scalar)(session, stmt=stmt)

    async def scalars(
        self, stmt: Select, session: AsyncSession | None = None
    ) -> ScalarResult:
        return await self.run_in_session(self._scalars)(session, stmt=stmt)

    async def add(
        self,
        schema: Type[DeclarativeMeta],
        autocommit: bool = False,
        refresh: bool = False,
        session: AsyncSession | None = None,
        **kwargs: Any,
    ) -> DeclarativeMeta:
        instance = schema(**kwargs)  # type: ignore
        return await self.run_in_session(self._add)(
            session, autocommit=autocommit, refresh=refresh, instance=instance
        )

    async def add_all(
        self,
        schema: Type[DeclarativeMeta],
        *args: dict,
        autocommit: bool = False,
        refresh: bool = False,
        session: AsyncSession | None = None,
    ) -> list[DeclarativeMeta]:
        instances = [schema(**arg) for arg in args]  # type: ignore
        return await self.run_in_session(self._add_all)(
            session, autocommit=autocommit, refresh=refresh, instances=instances
        )

    async def delete(
        self,
        instance: DeclarativeMeta,
        autocommit: bool = False,
        session: AsyncSession | None = None,
    ) -> DeclarativeMeta:
        return await self.run_in_session(self._delete)(
            session, autocommit=autocommit, instance=instance
        )

    async def scalars__fetchall(
        self, stmt: Select, session: AsyncSession | None = None
    ) -> list[DeclarativeMeta]:
        return (await self.run_in_session(self._scalars)(session, stmt=stmt)).fetchall()

    async def scalars__one(
        self, stmt: Select, session: AsyncSession | None = None
    ) -> DeclarativeMeta:
        return (await self.run_in_session(self._scalars)(session, stmt=stmt)).one()

    async def scalars__first(
        self, stmt: Select, session: AsyncSession | None = None
    ) -> DeclarativeMeta:
        return (await self.run_in_session(self._scalars)(session, stmt=stmt)).first()

    async def scalars__one_or_none(
        self, stmt: Select, session: AsyncSession | None = None
    ) -> Optional[DeclarativeMeta]:
        return (
            await self.run_in_session(self._scalars)(session, stmt=stmt)
        ).one_or_none()
