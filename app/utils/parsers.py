import requests
from requests import RequestException

from app.core.logging_config import logger
from app.schemas import repos


def parse_repos_top() -> list[repos.Repository]:
    url = "https://api.github.com/search/repositories"

    try:
        resp = requests.get(
            headers={
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            },
            url=url,
            params={
                "sort": "stars",
                "q": "stars:>0",
                "per_page": 100
            }
        )

        return [
            repos.Repository(
                repo=(repo := item.get("full_name")),
                owner=(owner := item.get("owner").get("login")),
                forks=item.get("forks"),
                watchers=item.get("watchers"),
                open_issues=item.get("open_issues"),
                language=item.get("language", None),
                position_prev=None,
                stars=item.get("stargazers_count"),
                position_cur=0,
            )
            for i, item in enumerate(resp.json().get("items"))
        ]

    except RequestException as e:
        logger.error(f"Can't parse data from {url}. Error: {e}")

    return list()
