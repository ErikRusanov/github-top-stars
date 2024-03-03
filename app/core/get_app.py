from fastapi import FastAPI, Request
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings
from app.routers.router import api_router
from app.services import repos_service, repo_activity_service
from app.utils import create_tables


def get_application() -> FastAPI:
    _app = FastAPI(title="Github Top Repositories")

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @_app.on_event("startup")
    async def on_startup():
        await create_tables(
            services=[
                repos_service,
                repo_activity_service
            ]
        )

    @_app.exception_handler(Exception)
    def _app_exception_handler(request: Request, e: Exception) -> JSONResponse:
        pass

    _app.include_router(api_router)
    return _app
