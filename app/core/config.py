from pydantic import PostgresDsn, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")

    # ------------- BASE --------------------------------------------
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    # ------------- DB ----------------------------------------------
    PSQL_URL: PostgresDsn

    # ------------- GITHUB JWT --------------------------------------
    TOKEN: str


settings = Settings()
