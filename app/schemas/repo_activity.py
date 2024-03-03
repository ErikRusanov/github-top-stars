from datetime import datetime, date

from pydantic import BaseModel


class RepoActivityBase(BaseModel):
    commits: int
    authors: list[str]


class RepoActivity(RepoActivityBase):
    date: date


class RepoActivityCreate(RepoActivityBase):
    date: date


class RepoActivityUpdate(RepoActivityBase):
    pass
