import re
from datetime import datetime, date

import requests
from requests import RequestException

from app.core import settings
from app.core.logging_config import logger
from app.schemas import repos, repo_activity


def _send_request(url: str, params: dict) -> tuple[dict, str | None]:
    try:
        resp = requests.get(
            headers={
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "Authorization": f"Bearer {settings.TOKEN}"
            },
            url=url,
            params=params
        )

        return resp.json(), resp.headers.get("Link", None)
    except RequestException as e:
        logger.error(f"Can't parse data from {url}. Error: {e}")

    return dict()


def parse_repos_top() -> list[repos.Repository]:
    data, _ = _send_request(
        url="https://api.github.com/search/repositories",
        params={
            "sort": "stars",
            "q": "stars:>0",
            "per_page": 100
        }
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


def parse_activity(
        repo_name: str,
        owner: str,
        latest_date: date | None
) -> list[repo_activity.RepoActivity]:
    url = f"https://api.github.com/repos/{owner}/{repo_name}/activity"
    data = list()

    while True:
        tmp_data, link = _send_request(
            url=url,
            params={
                "time_period": "year",
                "per_page": 100
            },
        )
        if not isinstance(tmp_data, list):
            break
        print(url, len(tmp_data))

        if latest_date and datetime.strptime(tmp_data[0].get("timestamp"), "%Y-%m-%dT%H:%M:%SZ").date() <= latest_date:
            break

        data.extend(tmp_data)

        if link is None:
            break
        if 'rel="next"' not in link:
            break

        if url := re.match(r"<https?://[^>]+after=[^>]+>", link):
            url = url.group()[1:-1]
        else:
            break

    return [
        (datetime.strptime(item.get("timestamp"), "%Y-%m-%dT%H:%M:%SZ").date(), item.get("actor").get("login"))
        for item in data
    ]
