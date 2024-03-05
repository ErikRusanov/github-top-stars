from collections import defaultdict
from datetime import date, datetime

from app.core.exceptions import DateRangeException, NoSuchRepository
from app.schemas import repo_activity
from app.services.base import BaseService
from app.services.repos import RepositoriesService, repos_service
from app.utils.ghp import github_parser


class RepositoryActivityService(BaseService):
    table_name = "repository_activity"
    schemaCU = repo_activity.RepoActivityCU
    _initial_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            commits INT NOT NULL,
            authors TEXT[] NOT NULL,
            repository_id INT REFERENCES {RepositoriesService.table_name}(id) NOT NULL,
            UNIQUE (date, repository_id)
        );
        CREATE INDEX IF NOT EXISTS idx_{table_name}_date ON {table_name} (date);
    """

    async def get_repo_activity(
            self,
            owner: str,
            repo: str,
            since: date,
            until: date
    ) -> list[repo_activity.RepoActivity]:
        if until < since:
            return list()

        if (until - since).days > 365 or (datetime.today().date() - until).days > 365:
            raise DateRangeException

        if (data := await repos_service.get_by_repo_and_owner(repo, owner, True)) is None:
            raise NoSuchRepository

        repository, just_created = data
        if just_created is None:
            await self.add_repo_activity(owner, repo, repository.id)

        latest_date_query = f"""
            SELECT MAX(date)
            FROM {self.table_name}
            WHERE repository_id = {repository.id};
        """
        latest_date = (await self.execute(latest_date_query, fetch=True))[0][0]
        # ! Important remark: for each repository, activity data is added once - in full,
        # then only if the date of the last update is not current

        if latest_date is None:
            # No data in database
            await self.add_repo_activity(owner, repo, repository.id)

        else:
            if latest_date <= until:
                await self.add_repo_activity(owner, repo, repository.id, latest_date)

        query = f"""
            SELECT * FROM {self.table_name}
            WHERE date >= '{since}' AND date <= '{until}' AND repository_id = {repository.id};
        """
        return [
            repo_activity.RepoActivity(**item)
            for item in await self.execute(query, fetch=True)
        ]

    async def add_repo_activity(
            self,
            owner: str,
            repo: str,
            repo_id: int,
            latest_date: date = None
    ) -> None:
        repo_name = repo.split("/")[-1]
        rpa = defaultdict(lambda: {"commits": 0, "authors": set()})
        for _date, author in github_parser.parse_activity(repo_name, owner, latest_date):
            rpa[_date]["commits"] += 1
            rpa[_date]["authors"].add(author)

        repo_activities = [
            repo_activity.RepoActivityCU(
                date=f"'{str(_date)}'",
                commits="'{}'".format(data.get("commits")),
                authors="ARRAY['{}']".format("', '".join(data["authors"])),
                repository_id=f"'{repo_id}'"
            )
            for _date, data in rpa.items()
        ]

        if repo_activities:
            await self.execute(
                self._insert_many_query(
                    values=[
                        self._format_data(item)
                        for item in repo_activities
                    ]
                )
            )


repo_activity_service = RepositoryActivityService()
