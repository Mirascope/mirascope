"""Base class for RAG prompts."""
from abc import ABC, abstractmethod

import pandas as pd
from pydantic import ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict

from mirascope import Prompt, messages


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    OPENAI_API_KEY: str
    PINECONE_API_KEY: str


@messages
class NewsRagPrompt(Prompt, ABC):
    """
    SYSTEM:
    You are an expert at:
    1) determining the relevancy of articles to a topic, and
    2) summarizing articles concisely and eloquently.

    When given a topic and a list of possibly relevant texts, you determine for each
    text if it is truly relevant to the topic, and only if so, do you summarize it. You
    format your responses as only a list, where each item is a summary of an article or
    an explanation as to why it is not relevant.

    USER:
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
