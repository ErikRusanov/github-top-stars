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


class RepositoryBase(BaseModel):
    position_cur: str
    position_prev: str
    stars: int
    watchers: int
    forks: int
    open_issues: int
    language: str


class Repository(RepositoryBase):
    repo: str
    owner: str


class RepositoryCreate(RepositoryBase):
    repo: str
    owner: str


class RepositoryUpdate(RepositoryBase):
    pass
