from app.schemas.repos import RepositorySort
from app.services.base import BaseService


class RepositoriesService(BaseService):
    table_name = "repositories"
    _initial_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id SERIAL PRIMARY KEY,
            repo VARCHAR NOT NULL,
            owner VARCHAR NOT NULL,
            position_cur INTEGER NOT NULL,
            position_prev INTEGER NOT NULL,
            stars INTEGER NOT NULL,          
            watchers INTEGER NOT NULL,
            forks INTEGER NOT NULL,           
            open_issues INTEGER NOT NULL,
            language VARCHAR NOT NULL,
            UNIQUE (owner, repo)
        );
        CREATE INDEX IF NOT EXISTS idx_{table_name}_owner_repo ON {table_name} (owner, repo);
    """

    async def get_top_repos_by_stars(self, sort: RepositorySort = None):
        query = f"""
            SELECT * FROM (
                SELECT * FROM {self.table_name}
                ORDER BY stars ASC
                LIMIT 100
            ) AS T
            {'ORDER BY {};'.format(sort.value) if sort else ';'}
        """

        return await self.execute(query, fetch=True)
