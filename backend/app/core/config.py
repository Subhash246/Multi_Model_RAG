"""
Centralized application configuration.

Every value here is overridable via environment variables (or a local
`.env` file — see `.env.example`). Nothing else in the codebase should
read `os.environ` directly; always go through `get_settings()` so there
is exactly one source of truth for configuration.
"""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # General
    app_name: str = "Multimodal RAG Platform"
    environment: str = Field(default="development")
    api_v1_prefix: str = "/api/v1"

    # CORS
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # LLM
    litellm_base_url: str = Field(
        default="http://localhost:4000"
    )
    litellm_api_key: str = Field(
        default="sk-local-dev-key"
    )
    default_model: str = Field(
        default="local-llama3"
    )
    request_timeout_seconds: int = Field(
        default=120
    )

    # File uploads
    max_upload_mb: int = Field(default=50)
    upload_dir: str = Field(default="./data/uploads")

    # Database
    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/multimodal_rag"
    )

    # MinIO
    minio_endpoint: str = Field(default="localhost:9000")
    minio_access_key: str = Field(default="minioadmin")
    minio_secret_key: str = Field(default="minioadmin")
    minio_bucket: str = Field(default="rag-documents")
    minio_secure: bool = Field(default=False)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Settings are cached so the .env file is only parsed once."""
    return Settings()
