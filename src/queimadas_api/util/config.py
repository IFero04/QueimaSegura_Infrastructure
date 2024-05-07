from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_port: str
    pg_host: str
    pg_port: str
    pg_db_name: str
    pg_user: str
    pg_password: str
    app_name: str = "Queimadas API"
    items_per_user: int = 50

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()