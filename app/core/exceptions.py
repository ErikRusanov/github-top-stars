from fastapi import Request
from starlette import status
from starlette.responses import JSONResponse


class DateRangeException(Exception):
    pass


class NoSuchRepository(Exception):
    pass


class RateLimitExceeded(Exception):
    pass


def handle_exception(request: Request, e: Exception) -> JSONResponse:
    if isinstance(e, RateLimitExceeded):
        status_code = status.HTTP_403_FORBIDDEN
        msg = "Exceeded API rate limit for github.com. Try again later"
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        msg = f"{type(e).__name__}: {e}"

    return JSONResponse(
        status_code=status_code,
        content={
            "message": msg
        }
    )
