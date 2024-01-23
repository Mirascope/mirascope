"""A basic prompt for asynchronously recommending books on a topic"""
import asyncio
import os

from mirascope import AsyncOpenAIChat, Prompt

os.environ["OPENAI_API_KEY"] = "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"


class BookRecommendationPrompt(Prompt):
    """
    Can you recommend some books on {topic}?
    """

    topic: str


prompt = BookRecommendationPrompt(topic="how to bake a cake")

model = AsyncOpenAIChat()


async def create_book_recommendation():
    """Asynchronously streams the response for a call to the model using `prompt`."""
    return await model.create(prompt)


print(asyncio.run(create_book_recommendation()))
