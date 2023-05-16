import asyncio
from datetime import datetime
from typing import AsyncGenerator, Generator
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
import httpx
import pytest_asyncio
from uuid import uuid4
from app import create_app
from app.logger import logging_config, CustomLogger
from gpt.cache_manager import ChatGptCacheManager
from database import cache


def random_user_generator():
    random_8_digits = str(hash(uuid4()))[:8]
    return {
        "email": f"{random_8_digits}@test.com",
        "password": "123",
        "name": f"{random_8_digits}",
        "phone_number": f"010{random_8_digits}",
    }


@pytest.fixture(scope="session")
def chatgpt_cache_manager():
    cache.start()
    return ChatGptCacheManager


@pytest.fixture(scope="session")
def test_logger():
    return CustomLogger(name="PyTest", logging_config=logging_config)


@pytest.fixture(scope="session")
def app() -> FastAPI:
    return create_app()


@pytest.fixture(scope="session")
def base_http_url() -> str:
    return "http://localhost"


@pytest.fixture(scope="session")
def base_websocket_url() -> str:
    return "ws://localhost"


@pytest_asyncio.fixture(scope="session")
async def real_client(
    app: FastAPI, base_http_url: str
) -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient(app=app, base_url=base_http_url) as ac:
        yield ac


@pytest.fixture(scope="session")
def websocket_app(app: FastAPI) -> Generator[TestClient, None, None]:
    with TestClient(app=app) as tc:
        yield tc


@pytest.fixture(scope="session")
def random_user():
    return random_user_generator()
