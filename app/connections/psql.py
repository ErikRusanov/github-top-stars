from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings

engine = create_async_engine(str(settings.PSQL_URL()))
AsyncSessionMaker = async_sessionmaker(engine, expire_on_commit=False)


# Async generator for providing async sessions
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provide an async session using the async session maker
    """
    async with AsyncSessionMaker() as session:
        yield session
