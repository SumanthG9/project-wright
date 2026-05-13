from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # PostgreSQL
    database_url: str
    alembic_database_url: str

    # MongoDB
    mongo_uri: str
    mongo_db: str = "project_wright"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Auth
    secret_key: str
    access_token_expire_minutes: int = 30

    # Ollama
    ollama_base_url: str = "http://localhost:11434"

    # Pipeline
    pipeline_mode: str = "local"
    local_model: str = "qwen3.5:4b"

    # Runtime
    environment: str = "development"
    debug: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # JWT
    jwt_algorithm: str = "HS256"
    refresh_token_expire_days: int = 7

    # Uploads
    upload_dir: str
    max_upload_size_mb: int


settings = Settings()
