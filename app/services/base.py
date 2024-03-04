from abc import ABC
from typing import Any

import asyncpg
from asyncpg import Pool, Connection

from app.core import settings
from app.core.logging_config import logger


class BaseService(ABC):
    table_name: str = ...
    _initial_query: str = ...

    def __init__(self):
        self._pool: Pool | None = None

    async def _create_pool(self) -> None:
        self._pool = await asyncpg.create_pool(dsn=str(settings.PSQL_URL))

    async def execute(
            self,
            query: str,
            *args,
            fetch: bool = False
    ) -> Any:
        try:
            async with self._pool.acquire() as conn:
                conn: Connection
                async with conn.transaction():
                    if fetch:
                        return await conn.fetch(query, *args)
                    else:
                        return await conn.execute(query, *args)
        except Exception as e:
            logger.error(f"Can't execute query:\n{query}\n\nError: {e}")

    async def create_table(self) -> None:
        await self._create_pool()
        await self.execute(self._initial_query)
