from fastapi import FastAPI, Request
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.core import settings
from app.routers import api_router
from app.services.repo_activity import repo_activity_service
from app.services.repos import repos_service
from app.utils.scheduler import configure_scheduler
from .logging_config import logger


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
        services = [
            repos_service,
            repo_activity_service
        ]
        for service in services:
            await service.create_table()

        logger.info("Database is ready for use")
        await repos_service.init_top_repos_on_startup()

    @_app.exception_handler(Exception)
    def _app_exception_handler(request: Request, e: Exception) -> JSONResponse:
        # Some extra handler logic

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "exception": f"{type(e).__name__}: {e}",
            }
        )

    _app.include_router(api_router)

    scheduler = configure_scheduler()
    scheduler.start()

    return _app
