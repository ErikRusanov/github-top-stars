from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query
from starlette import status
from starlette.responses import JSONResponse

from app.core.exceptions import DateRangeException, NoSuchRepository
from app.schemas import repo_activity
from app.services.repo_activity import repo_activity_service

repo_activity_router = APIRouter(
    prefix="/repo",
    tags=["Activity"]
)


@repo_activity_router.get(
    path="/{owner}/{repo:path}/activity",
    status_code=status.HTTP_200_OK,
    response_model=list[repo_activity.RepoActivity]
)
async def get_activity(
        owner: str,
        repo: str,
        since: Annotated[date, Query(example="2024-12-30")],
        until: Annotated[date, Query(example="2024-12-30")],
):
    try:
        return await repo_activity_service.get_repo_activity(
            owner=owner,
            repo=repo,
            since=since,
            until=until
        )
    except DateRangeException:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content="The commit history is only available for the last year. Max date range is 1 year"
        )

    except NoSuchRepository:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content="Can't find such repository")
