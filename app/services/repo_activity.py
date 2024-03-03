from app.services.base import BaseService


class RepositoryActivityService(BaseService):
    _initial_query = """
        CREATE TABLE IF NOT EXISTS repository_activity (
            id SERIAL PRIMARY KEY,
            date DATE NOT NULL,
            commits INT NOT NULL,
            authors TEXT[] NOT NULL,
            repository_id INT REFERENCES repositories(id) NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_repository_activity_date ON repository_activity (date);
    """
