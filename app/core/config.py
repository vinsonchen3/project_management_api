from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # auth
    secret_key: SecretStr
    algorithm: str
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    password_hash_scheme: str

    # database
    database_url: str
    test_database_url: str | None = None


settings = Settings()
