import asyncio

from app.core import settings
from app.core.logging_config import logger
from app.schemas import repos
from app.schemas.repos import RepositorySort
from app.services.base import BaseService
from app.utils.ghp import github_parser


class RepositoriesService(BaseService):
    """
    Service for handling repositories.
    """

    table_name = "repositories"
    schemaCU = repos.RepositoryCU

    def __init__(self):
        super().__init__()
        self._initial_query = f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id SERIAL PRIMARY KEY,
                repo VARCHAR NOT NULL,
                owner VARCHAR NOT NULL,
                position_cur INTEGER DEFAULT null,
                position_prev INTEGER DEFAULT null,
                stars INTEGER DEFAULT null,          
                watchers INTEGER DEFAULT null,
                forks INTEGER DEFAULT null,           
                open_issues INTEGER DEFAULT null,
                language VARCHAR DEFAULT null,
                UNIQUE (owner, repo)
            );
            CREATE INDEX IF NOT EXISTS idx_{self.table_name}_owner_repo ON {self.table_name} (owner, repo);
        """

    def _select_top_repos_query(
            self,
            sort: RepositorySort = None,
            sort_desc: bool = True,
            limit: int | None = 100
    ) -> str:
        """
        Generate SQL query for selecting top repositories by stars.

        :param sort: Sorting field.
        :param sort_desc: Sort in descending order.
        :param limit: Maximum number of repositories to retrieve.
        :return: SQL query.
        """

        order_by = f"{sort.value if sort else RepositorySort.stars.value} {'DESC' if sort_desc else 'ASC'}"
        limit_cond = f"LIMIT {limit}" if limit else ""

        return f"""
            SELECT * FROM (
                SELECT * FROM {self.table_name}
                WHERE position_cur IS NOT null AND stars IS NOT null
                ORDER BY {RepositorySort.stars.value} DESC
                {limit_cond}
            ) AS T
            ORDER BY {order_by};
        """

    def _select_query(self, repo: str, owner: str) -> str:
        """
        Generate SQL query for selecting a repository by repo and owner.

        :param repo: Repository name.
        :param owner: Owner name.
        :return: SQL query.
        """

        return f"""
            SELECT * FROM {self.table_name}
            WHERE repo = '{repo}' AND owner = '{owner}'
        """

    def _update_query(self, repo: repos.RepositoryCU) -> str:
        """
        Generate an update query for a repository.

        :param repo: Repository to be updated.
        :return: Update query.
        """

        return f"""
            UPDATE {self.table_name} SET {(
            ", ".join(
                [
                    f"{col} = {value}"
                    for col, value in zip(repos.RepositoryCU.model_fields.keys(), repo.model_dump().values())
                ]
            )
        )}
            WHERE repo = {repo.repo} AND owner = {repo.owner}
        """

    @staticmethod
    def _prepare_before_pushing(repos_list: list[repos.Repository]) -> list[repos.RepositoryCU]:
        """
        Prepare repositories before pushing.

        :param repos_list: List of repositories.
        :return: List of prepared repositories.
        """

        repos_dict = {
            (repo.repo, repo.owner): repo
            for repo in repos_list
        }
        sorted_repos = sorted(repos_dict.values(), key=lambda r: -r.stars)
        return [
            repos.RepositoryCU(
                repo=f"'{item.repo}'",
                owner=f"'{item.owner}'",
                forks=f"'{item.forks}'",
                watchers=f"'{item.watchers}'",
                open_issues=f"'{item.open_issues}'",
                language="'{}'".format(item.language) if item.language else "null",
                position_prev=f"'{item.position_cur}'" if item.position_cur else "null",
                stars=f"'{item.stars}'",
                position_cur=f"'{i + 1}'",
            )
            for i, item in enumerate(sorted_repos)
        ]

    @staticmethod
    def _repos_different(old_repo: repos.Repository, cur_repo: repos.RepositoryCU) -> bool:
        """
        Check if repositories are different.

        :param old_repo: Old repository.
        :param cur_repo: Current repository.
        :return: True if repositories are different, False otherwise.
        """

        return not all(
            (
                old_repo.repo == cur_repo.repo.strip("'"),
                old_repo.owner == cur_repo.owner.strip("'"),
                old_repo.stars == int(cur_repo.stars.strip("'")),
                old_repo.position_cur == int(cur_repo.position_cur.strip("'")),
                old_repo.open_issues == int(cur_repo.open_issues.strip("'")),
                old_repo.forks == int(cur_repo.forks.strip("'")),
                old_repo.watchers == int(cur_repo.watchers.strip("'")),
                (
                        old_repo.language is None and cur_repo.language == "null" or
                        old_repo.language == cur_repo.language.strip("'")
                ),
            )
        )

    async def get_top_repos_by_stars(
            self,
            sort: RepositorySort = None,
            sort_desc: bool = True,
            limit: int | None = 100
    ) -> list[repos.Repository]:
        """
        Get the top repositories by stars.

        :param sort: Sorting field.
        :param sort_desc: Sort in descending order.
        :param limit: Maximum number of repositories to retrieve.
        :return: List of repositories.
        """

        query = self._select_top_repos_query(sort, sort_desc, limit)

        return [
            repos.Repository(**item)
            for item in await self.execute(query, fetch=True)
        ]

    async def init_top_repos_on_startup(self) -> None:
        """
        Initialize top repositories on startup.
        """

        if settings.YCF_URL is not None:
            return

        old_repos = await self.get_top_repos_by_stars()
        if old_repos:
            return

        current_repos = github_parser.parse_top_repos()
        repos_to_push = self._prepare_before_pushing(current_repos)
        values = [self._format_data(repo) for repo in repos_to_push]
        query = self._insert_many_query(values)

        await self.execute(query)

    async def update_top_repos(self) -> None:
        """
        Update top repositories.
        """

        old_repos = await self.get_top_repos_by_stars(limit=None)
        old_repos_dict = {
            (repo.repo, repo.owner): repo
            for repo in old_repos
        }
        current_repos = github_parser.parse_top_repos()
        repos_to_push = self._prepare_before_pushing(old_repos + current_repos)

        tasks = list()
        columns = self._columns()

        for cur_repo in repos_to_push:
            old_repo = old_repos_dict.get((cur_repo.repo.strip("'"), cur_repo.owner.strip("'")), None)
            if old_repo:
                query = self._update_query(cur_repo) if self._repos_different(old_repo, cur_repo) else None
            else:
                query = self._insert_many_query([self._format_data(cur_repo)], columns)

            if query:
                tasks.append(self.execute(query))

        await asyncio.gather(*tasks)

        logger.info("Updated top repositories")

    async def get_by_repo_and_owner(
            self,
            repo: str,
            owner: str,
            create: bool = False
    ) -> tuple[repos.Repository, bool] | None:
        """
        Get repository by repo and owner.

        :param repo: Repository name.
        :param owner: Owner name.
        :param create: Create the repository if not exists.
        :return: Tuple containing the repository and a boolean indicating if it was created.
        """

        query = self._select_query(repo, owner)

        item = await self.execute(query, fetch=True)
        if item:
            return repos.Repository(**item[0]), False

        if not create:
            return

        await self.execute(
            self._insert_many_query(
                values=[
                    self._format_data(repos.RepositoryCU(
                        position_cur="null",
                        position_prev="null",
                        stars="null",
                        watchers="null",
                        forks="null",
                        open_issues="null",
                        language="null",
                        repo=f"'{repo}'",
                        owner=f"'{owner}'",
                    ))
                ]
            )
        )

        item = await self.execute(query, fetch=True)
        if item:
            return repos.Repository(**item[0]), True


repos_service = RepositoriesService()
