import os

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from app import chatroom, websockets
from app.dependencies import process_pool_executor
from app.globals import ALLOWED, LOG_DIR, TRUSTED
from app.logger import api_logger
from app.middlewares import TrustedHostMiddleware, exception_handler_middleware
from database import cache, db


def create_app() -> FastAPI:
    """
    Create directories if not exist
    """
    os.makedirs(LOG_DIR, exist_ok=True)
    with open(os.path.join(LOG_DIR, "app.log"), "a") as f:
        pass
    app = FastAPI(
        title="ResearchGPT",
        description="ResearchGPT is a tool for researchers to generate ideas and insights.",
        version="0.1.0",
    )
    db.start()
    cache.start()
    # Middlewares
    """
    Access control middleware: Authorized request only
    CORS middleware: Allowed sites only
    Trusted host middleware: Allowed host only
    """
    app.add_middleware(
        dispatch=exception_handler_middleware, middleware_class=BaseHTTPMiddleware
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=TRUSTED,
        except_path=["/docs", "/redoc", "/openapi.json"],
    )
    # Routers
    app.include_router(websockets.router, prefix="/ws", tags=["websocket"])
    app.include_router(
        chatroom.router,
        tags=["chatroom"],
    )

    @app.on_event("startup")
    async def startup():
        if db.is_initiated:
            api_logger.critical("MySQL DB connected!")
        else:
            api_logger.critical("MySQL DB connection failed!")
        if cache.redis is None:
            raise ConnectionError("Redis is not connected yet!")
        if cache.is_initiated and await cache.redis.ping():
            api_logger.critical("Redis CACHE connected!")
        else:
            api_logger.critical("Redis CACHE connection failed!")

    @app.on_event("shutdown")
    async def shutdown():
        process_pool_executor.shutdown()
        await db.close()
        await cache.close()
        api_logger.critical("DB & CACHE connection closed!")

    return app
