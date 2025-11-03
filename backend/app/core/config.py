from typing import Annotated

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # JWT Settings
    SECRET_KEY: Annotated[
        str,
        Field(
            default="your-secret-key-change-in-production-use-env-variable",
            description="Secret key for JWT token signing. Use environment variable SECRET_KEY in production.",
        ),
    ]
    ALGORITHM: Annotated[
        str,
        Field(
            default="HS256",
            description="Algorithm for JWT token signing",
        ),
    ]
    ACCESS_TOKEN_EXPIRE_MINUTES: Annotated[
        int,
        Field(
            default=30,
            ge=1,
            description="Access token expiration time in minutes",
        ),
    ]


settings = Settings()
