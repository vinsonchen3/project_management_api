from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # auth
    secret_key: SecretStr
    algorithm: str
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    password_hash_scheme: str

    # database
    database_url: str
    test_database_url: str | None = None


# import os

# print("SECRET_KEY exists:", "SECRET_KEY" in os.environ)
# print("ALGORITHM exists:", "ALGORITHM" in os.environ)
# print("PASSWORD_HASH_SCHEME exists:", "PASSWORD_HASH_SCHEME" in os.environ)
# print("DATABASE_URL exists:", "DATABASE_URL" in os.environ)
settings = Settings()
