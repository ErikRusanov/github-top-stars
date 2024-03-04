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
    position_cur: int
    position_prev: int | None
    stars: int
    watchers: int
    forks: int
    open_issues: int
    language: str | None


class Repository(_RepositoryBase):
    repo: str
    owner: str


class RepositoryCU(BaseModel):
    position_cur: str
    position_prev: str
    stars: str
    watchers: str
    forks: str
    open_issues: str
    language: str
    repo: str
    owner: str
