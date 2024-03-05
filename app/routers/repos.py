from fastapi import APIRouter, Query
from starlette import status

from app.schemas import repos
from app.services.repos import repos_service

repos_router = APIRouter(
    prefix="/repos",
    tags=["Top 100"]
)


@repos_router.get(
    path="/top100",
    status_code=status.HTTP_200_OK,
    response_model=list[repos.Repository],
    summary="Get top 100 repositories",
    description="Retrieve the top 100 repositories based on the specified sorting criteria.",
    response_description="List of Repository objects representing the top repositories.",
)
async def get_top_repos(
        sort: repos.RepositorySort = Query(None, description="Sorting criteria for the repositories."),
        sort_desc: bool = Query(True, description="Flag to indicate descending order if True."),
):
    """
    Retrieve the top 100 repositories based on the specified sorting criteria.

    :param sort: Sorting criteria for the repositories (optional).
    :param sort_desc: Flag to indicate descending order if True (default is True).
    :return: List of Repository objects representing the top repositories.
    """

    return await repos_service.get_top_repos_by_stars(sort, sort_desc)
