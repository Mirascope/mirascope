"""LangSmith + Mirascope example of extracting OpenAI chat to a structured output."""
import os

from langsmith import wrappers
from langsmith_config import Settings
from pydantic import BaseModel

from mirascope import OpenAIChat

settings = Settings()

os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
os.environ["LANGCHAIN_TRACING_V2"] = settings.langchain_tracing_v2
os.environ["OPENAI_API_KEY"] = settings.openai_api_key


class BookInfo(BaseModel):
    """A model for book info."""

    title: str
    author: str


chat = OpenAIChat(client_wrapper=wrappers.wrap_openai)
chat.extract(
    BookInfo,
    "The Name of the Wind is by Patrick Rothfuss.",
    retries=5,
)
