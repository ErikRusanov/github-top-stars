from datetime import date
from typing import Annotated

from fastapi import APIRouter, Query, Path
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
    response_model=list[repo_activity.RepoActivity],
    summary="Get repository activity",
    description="Retrieve the activity history of a repository within a specified date range.",
    response_description="List of RepoActivity objects representing the repository activity.",
)
async def get_activity(
        owner: Annotated[str, Path(example="jwasham")],
        repo: Annotated[str, Path(example="jwasham/coding-interview-university")],
        since: Annotated[date, Query(example="2024-01-01", description="Start date of the activity range.")],
        until: Annotated[date, Query(example="2024-12-30", description="End date of the activity range.")],
):
    """
    Retrieve the activity history of a repository within a specified date range.

    :param owner: Owner of the repository.
    :param repo: Name of the repository.
    :param since: Start date of the activity range.
    :param until: End date of the activity range.
    :return: List of RepoActivity objects representing the repository activity.
    """

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
