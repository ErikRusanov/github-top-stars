import re
from datetime import datetime, date
from typing import Any

import requests
from requests import RequestException

from app.core import settings
from app.core.exceptions import RateLimitExceeded
from app.core.logging_config import logger
from app.schemas import repos


class GHParser:
    """
    GitHub Parser class for handling GitHub data parsing.
    """

    def __init__(self):
        self._headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Authorization": f"Bearer {settings.TOKEN}"
        }

        self._search_repos_url = "https://api.github.com/search/repositories"
        self._search_repos_params = {
            "sort": "stars",
            "q": "stars:>0",
            "per_page": 100
        }

        self._list_repo_activity_url = "https://api.github.com/repos/{owner}/{repo_name}/activity"
        self._list_repo_activity_params = {
            "time_period": "year",
            "per_page": 100
        }

    def _send_request(self, url: str, params: dict) -> tuple[dict, str | None]:
        """
        Sends a request to the specified URL with parameters.

        :param url: The URL to send the request.
        :param params: Parameters to include in the request.
        :return: A tuple containing response data and header link.
        """

        try:
            resp = requests.get(
                headers=self._headers,
                url=url,
                params=params
            )

            data = resp.json()
            if isinstance(data, dict) and "API rate limit exceeded" in data.get("msg", ""):
                raise RateLimitExceeded

            return resp.json(), resp.headers.get("Link", None)
        except RequestException as e:
            logger.error(f"Can't parse data from {url}. Error: {e}")

        return dict(), None

    @staticmethod
    def _convert_date(item: dict) -> date:
        """
        Converts the timestamp from the GitHub API response to a date object.

        :param item: The GitHub API response item.
        :return: Date object extracted from the timestamp.
        """

        _format = "%Y-%m-%dT%H:%M:%SZ"
        return datetime.strptime(item.get("timestamp"), _format).date()

    def _next_url(self, data: Any, link: str, latest_date: date) -> str | None:
        """
        Determines the next URL for paginated responses based on the provided data and link.

        :param data: The data received from the GitHub API response.
        :param link: The link header from the GitHub API response.
        :param latest_date: The latest date to retrieve activity from.
        :return: The next URL if conditions are met, otherwise None.
        """

        if latest_date and self._convert_date(data[0]) <= latest_date:
            return

        if link is None or 'rel="next"' not in link:
            return

        if url := re.match(r"<https?://[^>]+after=[^>]+>", link):
            return url.group()[1:-1]

    def parse_activity(self, repo_name: str, owner: str, latest_date: date | None) -> list[tuple[date, str]]:
        """
        Parses activity for a given repository.

        :param repo_name: Name of the repository.
        :param owner: Owner of the repository.
        :param latest_date: The latest date to retrieve activity from.
        :return: A list of tuples containing date and actor login.
        """

        url = self._list_repo_activity_url.format(owner=owner, repo_name=repo_name)
        items = list()

        while True:
            data, link = self._send_request(
                url=url,
                params=self._list_repo_activity_params,
            )

            if not isinstance(data, list):
                break
            items.extend(data)

            if (url := self._next_url(data, link, latest_date)) is None:
                break

        return [
            (self._convert_date(item), item.get("actor").get("login"))
            for item in items
        ]

    def parse_top_repos(self) -> list[repos.Repository]:
        """
        Parses top repositories from GitHub.

        :return: A list of Repository objects.
        """

        data, _ = self._send_request(
            url=self._search_repos_url,
            params=self._search_repos_params
        )

        return [
            repos.Repository(
                repo=item.get("full_name"),
                owner=item.get("owner").get("login"),
                forks=item.get("forks"),
                watchers=item.get("watchers"),
                open_issues=item.get("open_issues"),
                language=item.get("language", None),
                position_prev=None,
                stars=item.get("stargazers_count"),
                position_cur=0,
            )
            for i, item in enumerate(items)
        ] if (items := data.get("items"), None) else list()


github_parser = GHParser()
