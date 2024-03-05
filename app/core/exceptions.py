from fastapi import Request
from starlette import status
from starlette.responses import JSONResponse


class DateRangeException(Exception):
    """
    Exception raised when the date range for a query is invalid or exceeds allowed limits.
    """
    pass


class NoSuchRepository(Exception):
    """
    Exception raised when attempting to access a non-existent repository.
    """
    pass


class RateLimitExceeded(Exception):
    """
    Exception raised when the API rate limit for gitHub.com is exceeded.
    """
    pass


def handle_exception(request: Request, e: Exception) -> JSONResponse:
    """
    Handles exceptions by returning an appropriate JSONResponse with status code and message.

    :param request: The FastAPI Request object.
    :param e: The exception object.
    :return: JSONResponse containing the error message and status code.
    """

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
