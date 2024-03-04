from datetime import date

from app.services.base import BaseService
from .repos import RepositoriesService
from ..utils.parsers import parse_activity


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

        if (until - since).days > 365:
            raise ValueError

        query = f"""
            SELECT * FROM {self.table_name}
            WHERE date >= '{since}' AND date <= '{until}' AND repository_id = (
                SELECT id FROM {RepositoriesService.table_name}
                WHERE owner = '{owner}' AND repo = '{repo}'
            );
        """

        return await self.execute(query, fetch=True) or await self.add_repo_activity(owner, repo, since, until)

    async def add_repo_activity(self, owner: str, repo: str, since: date, until: date) -> list:
        repo_name = repo.split("/")[-1]
        parse_activity(repo_name, owner, 2, (until - since).days)
        return list()
