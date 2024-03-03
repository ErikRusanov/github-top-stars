from abc import ABC
from typing import Any

import asyncpg
from asyncpg import Pool, Connection

from app.core import settings


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
        async with self._pool.acquire() as conn:
            conn: Connection
            async with conn.transaction():
                if fetch:
                    return await conn.fetch(query, *args)
                else:
                    return await conn.execute(query, *args)

    async def create_table(self) -> None:
        await self._create_pool()
        await self.execute(self._initial_query)
