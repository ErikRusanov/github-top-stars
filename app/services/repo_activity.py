from datetime import date

from app.services.base import BaseService
from .repos import RepositoriesService


class RepositoryActivityService(BaseService):
    table_name = "repository_activity"
    _initial_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            commits INT NOT NULL,
            authors TEXT[] NOT NULL,
            repository_id INT REFERENCES {RepositoriesService.table_name}(id) NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_{table_name}_date ON {table_name} (date);
    """

    async def get_repo_activity(
            self,
            owner: str,
            repo: str,
            since: date,
            until: date
    ) -> list[dict]:
        if until < since:
            return list()

        query = f"""
            SELECT * FROM {self.table_name}
            WHERE date >= '{since}' AND date <= '{until}' AND repository_id = (
                SELECT id FROM {RepositoriesService.table_name}
                WHERE owner = '{owner}' AND repo = '{repo}'
            );
        """

        return await self.execute(query, fetch=True)
