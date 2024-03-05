from datetime import date

from pydantic import BaseModel


class _RepoActivityBase(BaseModel):
    """
    Base Pydantic model for repository activity data.
    """

    commits: int
    authors: list[str]


class RepoActivity(_RepoActivityBase):
    """
    Pydantic model representing a repository activity with an additional 'date' field.
    """

    date: date


class RepoActivityCU(BaseModel):
    """
    Pydantic model for creating or updating repository activity data.
    """

    commits: str
    authors: str
    date: str
    repository_id: str
