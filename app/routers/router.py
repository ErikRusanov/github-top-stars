from fastapi import APIRouter

from app.routers.repo_activity import repo_activity_router
from app.routers.repos import repos_router

api_router = APIRouter(prefix="/api")

api_router.include_router(repos_router)
api_router.include_router(repo_activity_router)
