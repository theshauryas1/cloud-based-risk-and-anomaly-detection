"""
app/config.py — Application settings loaded from environment variables.
Falls back to SQLite for local development when DATABASE_URL is not set.
In production (ENV=production), DATABASE_URL MUST be set explicitly.
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    # ── Application ───────────────────────────────────────────
    ENV: str = "development"
    LOG_LEVEL: str = "INFO"

    # ── Database ──────────────────────────────────────────────
    # Leave blank locally → auto-uses SQLite
    # Set to Neon/Postgres URL in production
    DATABASE_URL: str = ""

    # ── Model artifacts ───────────────────────────────────────
    FRAUD_MODEL_PATH: str = "app/models/artifacts/fraud_model.pkl"
    ANOMALY_MODEL_PATH: str = "app/models/artifacts/anomaly_model.pkl"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def resolve_database_url(cls, v: str, info) -> str:
        """
        - production: DATABASE_URL must be set (raises if blank).
        - development/testing: falls back to SQLite.
        """
        env = (info.data or {}).get("ENV", "development")
        if not v:
            if env == "production":
                raise ValueError(
                    "DATABASE_URL must be set in production. "
                    "Set it to your Neon Postgres connection string."
                )
            return "sqlite:///./app/db/risk.db"
        return v

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
