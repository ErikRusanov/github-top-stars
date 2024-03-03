from app.services.base import BaseService


class RepositoriesService(BaseService):
    _initial_query = """
        CREATE TABLE IF NOT EXISTS repositories (
            id SERIAL PRIMARY KEY,
            repo VARCHAR NOT NULL,
            owner VARCHAR NOT NULL,
            position_cur INTEGER NOT NULL,
            position_prev INTEGER NOT NULL,
            stars INTEGER NOT NULL,          
            watchers INTEGER NOT NULL,
            forks INTEGER NOT NULL,           
            open_issues INTEGER NOT NULL,
            language VARCHAR NOT NULL,
            UNIQUE (owner, repo)
        );
        CREATE INDEX IF NOT EXISTS idx_repositories_owner_repo ON repositories (owner, repo);
    """
