from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ------------- BASE --------------------------------------------
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    # ------------- DB ----------------------------------------------
    PSQL_URL: PostgresDsn


settings = Settings()
