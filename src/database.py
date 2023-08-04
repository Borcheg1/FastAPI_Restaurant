from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER

DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'


class Base(DeclarativeBase):
    pass


engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Get AsyncSession for connect to db."""
    async with async_session() as session:
        yield session


async def create_tables() -> None:
    """Drop and recreate tables in db."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
