from app.schemas import repos
from app.schemas.repos import RepositorySort
from app.services.base import BaseService
from app.utils.parsers import parse_repos_top


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
            language VARCHAR,
            UNIQUE (owner, repo)
        );
        CREATE INDEX IF NOT EXISTS idx_{table_name}_owner_repo ON {table_name} (owner, repo);
    """

    async def get_top_repos_by_stars(
            self,
            sort: RepositorySort = None,
            sort_desc: bool = True
    ) -> list[dict]:
        order_by = f"{sort.value if sort else RepositorySort.stars.value} {'DESC' if sort_desc else 'ASC'}"
        query = f"""
            SELECT * FROM {self.table_name}
            ORDER BY {order_by};
        """

        return await self.execute(query, fetch=True)

    async def update_top_repos(self) -> None:
        current_repos = parse_repos_top()
        old_repos = await self.get_top_repos_by_stars()
        columns = ", ".join(repos.RepositoryCreate.model_fields.keys())

        if not old_repos:
            values = ["('{}')".format("', '".join(repo.model_dump().values())) for repo in current_repos]
            query = f"""
                INSERT INTO {self.table_name} ({columns}) VALUES {", ".join(values)}
            """
            await self.execute(query)
