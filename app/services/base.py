from abc import ABC
from typing import Any

import asyncpg
from asyncpg import Pool, Connection
from pydantic import BaseModel

from app.core import settings
from app.core.logging_config import logger


class BaseService(ABC):
    """
    Abstract base class for service layers interacting with a PostgreSQL database.
    """

    table_name: str = ...
    _initial_query: str = ...
    schemaCU: BaseModel

    def __init__(self):
        self._pool: Pool | None = None

    async def _create_pool(self) -> None:
        """
        Creates an asyncpg connection pool using the specified PostgreSQL URL.
        """

        self._pool = await asyncpg.create_pool(dsn=str(settings.PSQL_URL))

    async def execute(self, query: str, *args, fetch: bool = False) -> Any:
        """
        Executes a SQL query with optional fetch functionality.

        :param query: The SQL query to execute.
        :param args: Arguments to replace placeholders in the query.
        :param fetch: If True, fetch results; if False, execute without fetching results.
        :return: Result of the query execution.
        """
        if self._pool is None:
            await self._create_pool()

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

    async def close_connection(self) -> None:
        await self._pool.close()

    async def create_table(self) -> None:
        """
        Creates a table in the database using the initial query provided in the service.
        """

        await self.execute(self._initial_query)

    def _columns(self) -> str:
        """
        Returns a comma-separated string of column names in the associated database table.
        """

        return ", ".join(self.schemaCU.model_fields.keys())

    def _insert_many_query(self, values: list[str], columns: str = None) -> str:
        """
        Generates a SQL query for inserting multiple rows into the database table.

        :param values: List of value strings for each row.
        :param columns: Optional comma-separated string of column names.
        :return: SQL query for the bulk insert operation.
        """

        columns = columns or self._columns()
        return f"INSERT INTO {self.table_name} ({columns}) VALUES {', '.join(values)}"

    @staticmethod
    def _format_data(data: BaseModel) -> str:
        """
        Formats data from a Pydantic model into a string suitable for a SQL query.

        :param data: Pydantic model representing the data.
        :return: Formatted string of data.
        """

        return "({})".format(", ".join(data.model_dump().values()))
