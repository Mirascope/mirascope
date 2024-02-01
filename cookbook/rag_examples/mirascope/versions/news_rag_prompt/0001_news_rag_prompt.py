"""Base class for RAG prompts."""
from abc import ABC, abstractmethod

import pandas as pd
from pydantic import ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict

from mirascope import Prompt

prev_revision_id = "None"
revision_id = "0001"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    OPENAI_API_KEY: str
    PINECONE_API_KEY: str


class NewsRagPrompt(Prompt, ABC):
    """
    Here are {num_statements} article snippets about this topic: {topic}

    {context}

    Pick only the snippets which are truly relevant to the topic, and summarize them.
    """

    num_statements: int
    topic: str
    df: pd.DataFrame
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    @abstractmethod
    def context(self) -> str:
        """Finds most similar articles to topic using embeddings."""
        ...
