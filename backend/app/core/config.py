from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
import json


class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENVIRONMENT: str = "development"

    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "ai_expense_tracker"
    USE_MOCK_DB: str = "auto"  # "auto", "true", or "false"

    # Authentication & JWT
    JWT_SECRET_KEY: str = "dev_secret_jwt_key_at_least_32_chars_expense_tracker_secure_2026"
    JWT_REFRESH_SECRET_KEY: str = "dev_secret_refresh_key_at_least_32_chars_expense_tracker_2026"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    # Optional AI Key
    GEMINI_API_KEY: str = ""

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def check_production_secrets(self):
        """Audit secrets when running in production."""
        if self.ENVIRONMENT.lower() == "production":
            import logging
            log = logging.getLogger("expense_tracker.security")
            if "dev_secret" in self.JWT_SECRET_KEY:
                log.critical("SECURITY ALERT: Using insecure default JWT_SECRET_KEY in production mode!")
            if "dev_secret" in self.JWT_REFRESH_SECRET_KEY:
                log.critical("SECURITY ALERT: Using insecure default JWT_REFRESH_SECRET_KEY in production mode!")


settings = Settings()
settings.check_production_secrets()
