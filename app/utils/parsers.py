import requests

from app.schemas import repos


def parse_repos_top() -> list[repos.RepositoryCreate]:
    resp = requests.get(
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        },
        url="https://api.github.com/search/repositories",
        params={
            "sort": "stars",
            "q": "stars:>0",
            "per_page": 100
        }
    )

    return [
        repos.RepositoryCreate(
            repo=str(item.get("full_name")),
            owner=str(item.get("owner").get("login")),
            forks=str(item.get("forks")),
            watchers=str(item.get("watchers")),
            open_issues=str(item.get("open_issues")),
            language=str(item.get("language", None)),
            position_prev=str(0),
            position_cur=str(i),
            stars=str(item.get("stargazers_count"))
        )
        for i, item in enumerate(resp.json().get("items"))
    ]
