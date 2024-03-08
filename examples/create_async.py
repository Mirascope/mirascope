"""A basic prompt for asynchronously recommending books on a topic"""
import asyncio
import os

from mirascope.openai import OpenAIPrompt

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


class BookRecommendationPrompt(OpenAIPrompt):
    """
    Can you recommend some books on {topic}?
    """

    topic: str


prompt = BookRecommendationPrompt(topic="how to bake a cake")


async def create_book_recommendation():
    """Asynchronously creates the response for a chat completion."""
    return await prompt.async_create()


print(asyncio.run(create_book_recommendation()))
