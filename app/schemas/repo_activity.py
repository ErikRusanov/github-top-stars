from datetime import date

from pydantic import BaseModel


class _RepoActivityBase(BaseModel):
    commits: int
    authors: list[str]


class RepoActivity(_RepoActivityBase):
    date: date


class RepoActivityCreate(_RepoActivityBase):
    date: date


class RepoActivityUpdate(_RepoActivityBase):
    pass
