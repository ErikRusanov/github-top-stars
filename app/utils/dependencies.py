from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.connections.psql import get_async_session


class Deps:
    session: Annotated[AsyncSession, Depends(get_async_session)]


deps = Deps()
