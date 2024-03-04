"""Global variables for LangSmith examples."""
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str = ""
    langchain_tracing_v2: Literal["true"] = "true"
    langchain_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env")
