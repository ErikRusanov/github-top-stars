import requests
from requests import RequestException

from app.core.logging_config import logger
from app.schemas import repos, repo_activity


def _send_request(url: str, params: dict) -> dict:
    try:
        resp = requests.get(
            headers={
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            },
            url=url,
            params=params
        )
        return resp.json()
    except RequestException as e:
        logger.error(f"Can't parse data from {url}. Error: {e}")

    return dict()


def parse_repos_top() -> list[repos.Repository]:
    data = _send_request(
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


def parse_activity(repo_name: str, owner: str, page: int, days_delta: int) -> list[repo_activity.RepoActivity]:
    time_periods = {
        1: "day",
        7: "week",
        30: "month",
        90: "quarter"
    }
    data = _send_request(
        url=f"https://api.github.com/repos/{owner}/{repo_name}/activity",
        params={
            "page": page,
            "time_period": time_periods.get(days_delta, None) or "year",
            "per_page": 100
        }
    )
    # data = _send_request(
    #     url="https://api.github.com/search/commits",
    #     params={
    #         "per_page": 100,
    #         "q": "Q"
    #         # "q": f"items:repository:full_name:{owner}/{repo_name}"
    #     }
    # )
    result = [
        (item.get("timestamp"), item.get("actor").get("login"))
        for item in data
    ]
    print(result)
    return list()
