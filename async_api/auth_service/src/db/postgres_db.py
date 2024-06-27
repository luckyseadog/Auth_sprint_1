from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from core.config import settings

Base = declarative_base()

dsn = (
    f'postgresql+asyncpg://{settings.pg_user}'
    f':{settings.pg_password}@{settings.pg_host}'
    f':{settings.pg_port}/{settings.pg_name}'
)
engine = create_async_engine(dsn, echo=True, future=True)

async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def create_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def purge_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
