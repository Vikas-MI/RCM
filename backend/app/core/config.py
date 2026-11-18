from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment / .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Smart RCM Eligibility"
    app_env: str = "development"
    log_level: str = "INFO"

    database_url: str = (
        "postgresql+psycopg://postgres:password@localhost:5432/smart_rcm_eligibility"
    )

    hapi_fhir_base_url: str = "https://hapi.fhir.org/baseR4"
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
