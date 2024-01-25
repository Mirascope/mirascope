"""A basic prompt for asynchronously streaming book recommendations on a topic"""
import asyncio
import os

from mirascope import AsyncOpenAIChat, Prompt

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


class BookRecommendationPrompt(Prompt):
    """
    Can you recommend some books on {topic}?
    """

    topic: str


prompt = BookRecommendationPrompt(topic="how to bake a cake")

model = AsyncOpenAIChat()


async def stream_book_recommendation():
    """Asynchronously streams the response for a call to the model using `prompt`."""
    astream = model.stream(prompt)
    async for chunk in astream:
        print(chunk, end="")


asyncio.run(stream_book_recommendation())
