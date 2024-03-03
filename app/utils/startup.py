from app.services.base import BaseService
from .logging_config import logger


async def create_tables(services: list[BaseService]) -> None:
    for service in services:
        await service.create_table()

    logger.info("Database is ready for use")
