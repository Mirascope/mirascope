"""LangSmith + Mirascope example of OpenAI chat create."""
import os

from langsmith import wrappers
from langsmith_config import Settings

from mirascope import OpenAICallParams, OpenAIChat, Prompt

settings = Settings()

os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
os.environ["LANGCHAIN_TRACING_V2"] = settings.langchain_tracing_v2
os.environ["OPENAI_API_KEY"] = settings.openai_api_key


class BookRecommendationPrompt(Prompt):
    """
    Can you recommend some books on {topic}?
    """

    topic: str

    call_params = OpenAICallParams(model="gpt-3.5-turbo", temperature=0.1)


prompt = BookRecommendationPrompt(topic="how to bake a cake")
chat = OpenAIChat(client_wrapper=wrappers.wrap_openai)
completion = chat.create(prompt)
print(completion)
