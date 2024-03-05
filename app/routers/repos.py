from fastapi import APIRouter
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
    response_model=list[repos.Repository]
)
async def get_top_repos(
        sort: repos.RepositorySort = None,
        sort_desc: bool = True,
):
    return await repos_service.get_top_repos_by_stars(sort, sort_desc)
