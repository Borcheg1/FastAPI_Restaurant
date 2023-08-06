import asyncio
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import (
    TEST_DB_HOST,
    TEST_DB_NAME,
    TEST_DB_PASS,
    TEST_DB_PORT,
    TEST_DB_USER,
    TEST_REDIS_HOST,
    TEST_REDIS_PORT,
)
from src.database import Base, get_async_session, get_redis_client
from src.main import app

path = (
    f'postgresql+asyncpg://'
    f'{TEST_DB_USER}:{TEST_DB_PASS}@{TEST_DB_HOST}:{TEST_DB_PORT}/{TEST_DB_NAME}'
)
TEST_DATABASE_URL = path
redis_test = Redis(host=TEST_REDIS_HOST, port=TEST_REDIS_PORT, db=0)

test_engine = create_async_engine(TEST_DATABASE_URL)
test_async_session = async_sessionmaker(test_engine)


async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_async_session() as session:
        yield session


async def override_get_redis_client() -> AsyncGenerator[Redis, None]:
    async with redis_test as client:
        yield client


app.dependency_overrides[get_async_session] = override_get_async_session
app.dependency_overrides[get_redis_client] = override_get_redis_client


@pytest.fixture(scope='session')
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url=f'https://{TEST_DB_USER}/api/v1/') as ac:
        yield ac


@pytest_asyncio.fixture(scope='module', autouse=True)
async def prepare_tables() -> AsyncGenerator[AsyncClient, Redis]:
    async with redis_test as redis:
        await redis.flushdb()
    async with test_engine.begin() as con:
        await con.run_sync(Base.metadata.drop_all)
        await con.run_sync(Base.metadata.create_all)
    yield
    async with redis_test as redis:
        await redis.flushdb()
    async with test_engine.begin() as con:
        await con.run_sync(Base.metadata.drop_all)
        await con.run_sync(Base.metadata.create_all)
