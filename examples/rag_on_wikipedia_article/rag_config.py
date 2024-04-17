"""Config for RAG on Wikipedia Article."""
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    pinecone_api_key: Optional[str] = None
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
