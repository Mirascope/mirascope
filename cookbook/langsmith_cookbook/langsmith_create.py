"""LangSmith + Mirascope example of OpenAI chat create."""
import os

from langsmith import wrappers
from langsmith_config import Settings

from mirascope.openai import OpenAICallParams, OpenAIPrompt

settings = Settings()

os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
os.environ["LANGCHAIN_TRACING_V2"] = settings.langchain_tracing_v2
os.environ["OPENAI_API_KEY"] = settings.openai_api_key


class BookRecommendation(OpenAIPrompt):
    """
    Can you recommend some books on {topic}?
    """

    topic: str

    call_params = OpenAICallParams(
        model="gpt-3.5-turbo", temperature=0.1, wrapper=wrappers.wrap_openai
    )


book_recommendation = BookRecommendation(topic="how to bake a cake")
completion = book_recommendation.create()
print(completion)
