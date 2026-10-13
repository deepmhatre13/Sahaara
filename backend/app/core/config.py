from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        extra="ignore",
    )

    environment: str = "development"
    secret_key: str = "dev-secret"
    api_v1_prefix: str = "/api"

    database_url: str = "postgresql+psycopg2://sahaara:sahaara@localhost:5432/sahaara"

    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    gemini_api_key: str | None = None
    gemini_chat_model: str = "gemini-2.5-flash"
    gemini_embedding_model: str = "models/embedding-001"

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_collection: str = "medical_knowledge"

    notification_provider: str = "console"
    twilio_account_sid: str | None = None
    twilio_auth_token: str | None = None
    twilio_whatsapp_from: str | None = None
    twilio_whatsapp_to: str | None = None
    # WhatsApp Content Template SID (``HX...``). Required by Twilio for every
    # WhatsApp outbound message; without it Twilio rejects the request with
    # error 21654 (``ContentSid Required``). Leave unset in development to
    # get a graceful "not configured" failure instead of a crash.
    twilio_whatsapp_content_sid: str | None = None

    motion_provider: str = "mock"
    motion_camera_index: int = 0
    inactivity_threshold_seconds: int = 1800
    motion_poll_interval_seconds: int = 5

    health_data_provider: str = "mock"
    fitbit_client_id: str | None = None
    fitbit_client_secret: str | None = None

    ocr_provider: str = "mock"
    mistral_api_key: str | None = None

    cors_origins: str = "http://localhost:5173"

    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

  
    google_client_id: str | None = None


    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()