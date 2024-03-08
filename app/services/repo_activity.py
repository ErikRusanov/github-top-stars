from collections import defaultdict
from datetime import date, datetime

from app.core import settings
from app.core.exceptions import DateRangeException, NoSuchRepository
from app.schemas import repo_activity, repos
from app.services.base import BaseService
from app.services.repos import RepositoriesService, repos_service
from app.utils.ghp import github_parser
from app.utils.ycf import send_request_to_yandex_cloud_function


class RepositoryActivityService(BaseService):
    """
    Service for handling repository activity data.
    """

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
        CREATE INDEX IF NOT EXISTS idx_{table_name}_date ON {table_name} (repository_id);
    """

    def _select_in_date_range_query(self, repo_id: int, since: date, until: date) -> str:
        """
        Generate SQL query to select repository activities in a given date range.

        :param repo_id: Repository ID.
        :param since: Start date.
        :param until: End date.
        :return: SQL query.
        """

        return f"""
            SELECT * FROM {self.table_name}
            WHERE date >= '{since}' AND date <= '{until}' AND repository_id = {repo_id};
        """

    def _latest_date_query(self, repo_id: int) -> int:
        """
        Generate SQL query to get the latest date for a repository.

        :param repo_id: Repository ID.
        :return: SQL query.
        """

        return f"""
            SELECT MAX(date)
            FROM {self.table_name}
            WHERE repository_id = {repo_id};
        """

    @staticmethod
    def _date_range_is_valid(since: date, until: date) -> bool:
        """
        Check if the date range is valid.

        :param since: Start date.
        :param until: End date.
        :raises DateRangeException: If the date range is invalid.
        :return: True if the date range is valid, False otherwise.
        """

        if until < since:
            return False

        if (until - since).days > 365 or (datetime.today().date() - until).days > 365:
            raise DateRangeException

        return True

    @staticmethod
    def _prepare_before_pushing(
            owner: str,
            repo: str,
            repo_id: int,
            latest_date: date
    ) -> list[repo_activity.RepoActivityCU]:
        """
        Prepare repository activity data before pushing to the database.

        :param owner: Owner of the repository.
        :param repo: Repository name.
        :param repo_id: Repository ID.
        :param latest_date: Latest date for the repository.
        :return: List of prepared repository activities.
        """
        repo_name = repo.split("/")[-1]

        repo_activities = defaultdict(lambda: {"commits": 0, "authors": set()})
        data = send_request_to_yandex_cloud_function(
            data={
                "owner": owner,
                "repo_name": repo_name,
                "latest_date": latest_date
            },
            params={
                "action": "parse_activity"
            }
        ) if settings.YCF_URL else github_parser.parse_activity(repo_name, owner, latest_date)

        for _date, author in data:
            key = str(github_parser.convert_date(_date))
            repo_activities[key]["commits"] += 1
            repo_activities[key]["authors"].add(author)

        return [
            repo_activity.RepoActivityCU(
                date=f"'{_date}'",
                commits="'{}'".format(data.get("commits")),
                authors="ARRAY['{}']".format("', '".join(data["authors"])),
                repository_id=f"'{repo_id}'"
            )
            for _date, data in repo_activities.items()
        ]

    async def _update_repository_activity(self, repo: str, owner: str, until: date) -> repos.Repository:
        """
        Update repository activity data.

        Important remark: for each repository, activity data is added once - in full,
        then only if the date of the last update is not current

        :param repo: Repository name.
        :param owner: Owner of the repository.
        :param until: End date for updating activity data.
        :raises NoSuchRepository: If the repository doesn't exist.
        :return: Updated repository.
        """

        if (data := await repos_service.get_by_repo_and_owner(repo, owner, True)) is None:
            raise NoSuchRepository

        repository, just_created = data
        if just_created is None:
            await self.add_repo_activity(owner, repo, repository.id)
            return repository

        latest_date_query = self._latest_date_query(repository.id)
        latest_date = (await self.execute(latest_date_query, fetch=True))[0][0]

        await self.add_repo_activity(
            owner, repo, repository.id, latest_date if latest_date and latest_date <= until else None
        )
        return repository

    async def get_repo_activity(
            self,
            owner: str,
            repo: str,
            since: date,
            until: date
    ) -> list[repo_activity.RepoActivity]:
        """
        Get repository activity data in a given date range.

        :param owner: Owner of the repository.
        :param repo: Repository name.
        :param since: Start date.
        :param until: End date.
        :return: List of repository activities.
        """

        if not self._date_range_is_valid(since, until):
            return list()

        repository = await self._update_repository_activity(repo, owner, until)

        query = self._select_in_date_range_query(repository.id, since, until)
        return [
            repo_activity.RepoActivity(**item)
            for item in await self.execute(query, fetch=True)
        ]

    async def add_repo_activity(self, owner: str, repo: str, repo_id: int, latest_date: date = None) -> None:
        """
        Add repository activity data to the database.

        :param owner: Owner of the repository.
        :param repo: Repository name.
        :param repo_id: Repository ID.
        :param latest_date: Latest date for updating activity data.
        """
        if repo_activities := self._prepare_before_pushing(owner, repo, repo_id, latest_date):
            await self.execute(
                self._insert_many_query(
                    values=[
                        self._format_data(item)
                        for item in repo_activities
                    ]
                )
            )


repo_activity_service = RepositoryActivityService()
