from enum import Enum

from pydantic import BaseModel


class RepositorySort(Enum):
    """
    Enum representing sorting options for repositories.
    """

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
    """
    Base Pydantic model for repository data.
    """

    position_cur: int | None = None
    position_prev: int | None = None
    stars: int | None = None
    watchers: int | None = None
    forks: int | None = None
    open_issues: int | None = None
    language: str | None = None


class Repository(_RepositoryBase):
    """
    Pydantic model representing a repository with additional 'id', 'repo', and 'owner' fields.
    """

    id: int | None = None
    repo: str
    owner: str


class RepositoryCU(BaseModel):
    """
    Pydantic model for creating or updating repository data.
    """

    position_cur: str
    position_prev: str
    stars: str
    watchers: str
    forks: str
    open_issues: str
    language: str
    repo: str
    owner: str
