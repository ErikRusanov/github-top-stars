import asyncio

from app.schemas import repos
from app.schemas.repos import RepositorySort
from app.services.base import BaseService
from app.utils.parsers import parse_repos_top


class RepositoriesService(BaseService):
    table_name = "repositories"
    schemaCU = repos.RepositoryCU
    _initial_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
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
        CREATE INDEX IF NOT EXISTS idx_{table_name}_owner_repo ON {table_name} (owner, repo);
    """

    async def get_top_repos_by_stars(
            self,
            sort: RepositorySort = None,
            sort_desc: bool = True,
            limit: int | None = 100
    ) -> list[repos.Repository]:
        order_by = f"{sort.value if sort else RepositorySort.stars.value} {'DESC' if sort_desc else 'ASC'}"
        limit_cond = f"LIMIT {limit}" if limit else ""
        query = f"""
            SELECT * FROM (
                SELECT * FROM {self.table_name}
                WHERE position_cur IS NOT null AND stars IS NOT null
                ORDER BY {RepositorySort.stars.value} DESC
                {limit_cond}
            ) AS T
            ORDER BY {order_by};
        """

        return [
            repos.Repository(**item)
            for item in await self.execute(query, fetch=True)
        ]

    @staticmethod
    def _prepare_before_pushing(repos_list: list[repos.Repository]) -> list[repos.RepositoryCU]:
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

    async def init_top_repos_on_startup(self) -> None:
        old_repos = await self.get_top_repos_by_stars()
        if old_repos:
            return

        current_repos = parse_repos_top()
        repos_to_push = self._prepare_before_pushing(current_repos)
        values = [self._format_data(repo) for repo in repos_to_push]
        query = self._insert_many_query(values)

        await self.execute(query)

    @staticmethod
    def _repos_different(old_repo: repos.Repository, cur_repo: repos.RepositoryCU) -> bool:
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

    def _update_query(self, repo: repos.RepositoryCU) -> str:
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

    async def update_top_repos(self) -> None:
        old_repos = await self.get_top_repos_by_stars(limit=None)
        old_repos_dict = {
            (repo.repo, repo.owner): repo
            for repo in old_repos
        }
        current_repos = parse_repos_top()
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

    async def get_by_repo_and_owner(
            self,
            repo: str,
            owner: str,
            create: bool = False
    ) -> tuple[repos.Repository, bool] | None:
        query_select = f"""
            SELECT * FROM {self.table_name}
            WHERE repo = '{repo}' AND owner = '{owner}'
        """

        item = await self.execute(query_select, fetch=True)
        if item:
            return repos.Repository(**item[0]), False

        if not create:
            return None

        result = await self.execute(
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

        item = await self.execute(query_select, fetch=True)
        if item:
            return repos.Repository(**item[0]), True


repos_service = RepositoriesService()
