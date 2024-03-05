from datetime import date

from pydantic import BaseModel


class _RepoActivityBase(BaseModel):
    commits: int
    authors: list[str]


class RepoActivity(_RepoActivityBase):
    date: date


class RepoActivityCU(BaseModel):
    commits: str
    authors: str
    date: str
    repository_id: str
