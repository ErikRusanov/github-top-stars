from enum import Enum

from pydantic import BaseModel


class RepositorySort(Enum):
    position_cur: str = "position_cur"
    position_prev: str = "position_prev"
    stars: str = "stars"
    watchers: str = "watchers"
    forks: str = "forks"
    open_issues: str = "open_issues"
    language: str = "language"
    repo: str = "repo"
    owner: str = "owner"


class _RepositoryBase(BaseModel):
    position_cur: int | str
    position_prev: int | str
    stars: int | str
    watchers: int | str
    forks: int | str
    open_issues: int | str
    language: str | None


class Repository(_RepositoryBase):
    repo: str
    owner: str


class RepositoryCreate(_RepositoryBase):
    repo: str
    owner: str


class RepositoryUpdate(_RepositoryBase):
    pass
