from app.services.base import BaseService
from .repos import RepositoriesService


class RepositoryActivityService(BaseService):
    table_name = "repository_activity"
    _initial_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            commits INT NOT NULL,
            authors TEXT[] NOT NULL,
            repository_id INT REFERENCES {RepositoriesService.table_name}(id) NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_{table_name}_date ON {table_name} (date);
    """
