"""Configuration settings for the API."""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLMs
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # External APIs
    aemet_api_key: str = ""
    mapbox_access_token: str = ""

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


@lru_cache
def get_settings() -> Settings:
    return Settings()
