"""Configuration settings for the API."""

from functools import lru_cache
import anthropic
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLMs
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # Models
    model_sonnet: str = "claude-sonnet-4-6"
    model_opus: str = "claude-opus-4-7"
    model_haiku: str = "claude-haiku-4-5-20251001"

    # External APIs
    aemet_api_key: str = ""
    mapbox_access_token: str = ""
    mapillary_access_token: str = ""
    overpass_url: str = "https://overpass-api.de/api/interpreter"
    open_elevation_url: str = "https://api.open-elevation.com/api/v1/lookup"
    open_meteo_url: str = "https://archive-api.open-meteo.com/v1/archive"
    boe_search_url: str = "https://www.boe.es/datosabiertos/api"

    # Storage
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    r2_account_id: str = ""
    r2_access_key_id: str = ""
    r2_secret_access_key: str = ""
    r2_bucket: str = "veridict-uploads"

    # Vector DB
    qdrant_url: str = ""
    qdrant_api_key: str = ""
    qdrant_collection: str = "corpus_trafico_es"

    # Database
    database_url: str = ""

    # API
    api_base_url: str = "http://localhost:8000"

    # Sigstore
    sigstore_rekor_url: str = "https://rekor.sigstore.dev"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_claude() -> anthropic.AsyncAnthropic:
    settings = get_settings()
    return anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
