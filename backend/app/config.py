import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    DATABASE_URL: str = "sqlite+aiosqlite:///./find_job.db"
    CORS_ORIGINS: str = "http://localhost:5173"
    API_PREFIX: str = "/api"

    # GitHub Integration
    GITHUB_TOKEN: str = ""

    # Claude AI (MiniMax Claude-compatible endpoint)
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_BASE_URL: str = "https://api.minimaxi.com/anthropic"
    CLAUDE_MODEL: str = "MiniMax-M2.5-highspeed"


settings = Settings()
