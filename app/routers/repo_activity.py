from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query
from starlette import status

from app.schemas import repo_activity
from app.services import repo_activity_service

repo_activity_router = APIRouter(
    prefix="/repo",
    tags=["Activity"]
)


@repo_activity_router.get(
    path="/{owner}/{repo}/activity",
    status_code=status.HTTP_200_OK,
    response_model=list[repo_activity.RepoActivity]
)
async def get_activity(
        owner: str,
        repo: str,
        since: Annotated[date, Query(example="2024-12-30")],
        until: Annotated[date, Query(example="2024-12-30")],
):
    return await repo_activity_service.get_repo_activity(
        owner=owner,
        repo=repo,
        since=since,
        until=until
    )
