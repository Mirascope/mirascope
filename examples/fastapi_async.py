"""An asynchronous FastAPI app integrated with a multi-chain prompt.

The root API endpoint first recommends some books on a topic and then narrows the list 
down with the most beginner friendly.

How to Run:

    uvicorn api_example:app --reload
"""
import os

from fastapi import FastAPI

from mirascope.openai import OpenAIPrompt

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

app = FastAPI()


class BookRecommendationPrompt(OpenAIPrompt):
    """
    Can you recommend some books on {topic} in a list format?
    """

    topic: str


class BestForBeginnersPrompt(OpenAIPrompt):
    """
    Given this list {book_list}, which one is the best for beginners?
    """

    book_list: str


@app.post("/")
async def root(book_recommendation: BookRecommendationPrompt):
    """Generates the best book for beginners on the given topic."""
    book_list = await book_recommendation.async_create()

    best_for_beginners_prompt = BestForBeginnersPrompt(book_list=str(book_list))
    best_for_beginners = await best_for_beginners_prompt.async_create()
    return str(best_for_beginners)
