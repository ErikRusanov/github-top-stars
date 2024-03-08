from pydantic import PostgresDsn, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")

    # ------------- BASE --------------------------------------------
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    # ------------- DB ----------------------------------------------
    PSQL_URL: PostgresDsn

    # ------------- OTHER -------------------------------------------
    YCF_URL: str | None = None
    TOKEN: str | None = None

    def __init__(self):
        super().__init__()
        assert not (self.YCF_URL is None and self.TOKEN is None), "One of the parameters is required: YCF_URL or TOKEN"


settings = Settings()
