from fastapi import FastAPI, Request
from starlette import status
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings
from app.routers.router import api_router


def get_application() -> FastAPI:
    _app = FastAPI(title="Github Top Repositories")

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @_app.exception_handler(Exception)
    def _app_exception_handler(request: Request, e: Exception) -> JSONResponse:
        pass

    _app.include_router(api_router)

    return _app
