from typing import AsyncGenerator

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import (
    DB_HOST,
    DB_NAME,
    DB_PASS,
    DB_PORT,
    DB_USER,
    REDIS_HOST,
    REDIS_PORT,
)

DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
redis = Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)


class Base(DeclarativeBase):
    pass


engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get AsyncSession for connect to db."""
    async with async_session() as session:
        yield session


async def get_redis_client() -> AsyncGenerator[Redis, None]:
    async with redis as client:
        yield client


async def create_tables() -> None:
    """Drop and recreate tables in db"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


async def delete_cache() -> None:
    """Clear all cache in redis"""
    async with redis as client:
        await client.flushdb()
