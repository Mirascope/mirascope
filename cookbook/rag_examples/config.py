"""Global variables for RAG examples."""
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

MODEL = "gpt-3.5-turbo"
EMBEDDINGS_MODEL = "text-embedding-ada-002"
MAX_TOKENS = 1000
TEXT_COLUMN = "Text"
EMBEDDINGS_COLUMN = "embeddings"
FILENAME = "news_article_dataset.pkl"
URL = "https://raw.githubusercontent.com/Dawit-1621/BBC-News-Classification/main/Data/BBC%20News%20Test.csv"
PINECONE_INDEX = "news-articles"
PINECONE_NAMESPACE = "articles"


class Settings(BaseSettings):
    openai_api_key: Optional[str] = None
    pinecone_api_key: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env")
