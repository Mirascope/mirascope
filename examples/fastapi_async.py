"""An asynchronous FastAPI app integrated with a multi-chain prompt.

The root API endpoint first recommends some books on a topic and then narrows the list 
down with the most beginner friendly.

How to Run:

    uvicorn api_example:app --reload
"""
import os

from fastapi import FastAPI

from mirascope import AsyncOpenAIChat, BasePrompt

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"

app = FastAPI()


class BookRecommendationPrompt(BasePrompt):
    """
    Can you recommend some books on {topic} in a list format?
    """

    topic: str


class BestForBeginnersPrompt(BasePrompt):
    """
    Given this list {book_list}, which one is the best for beginners?
    """

    book_list: str


@app.post("/")
async def root(book_recommendation: BookRecommendationPrompt):
    """Generates the best book for beginners on the given topic."""
    model = AsyncOpenAIChat()
    book_list = await model.create(book_recommendation)

    best_for_beginners_prompt = BestForBeginnersPrompt(book_list=str(book_list))
    best_for_beginners = await model.create(best_for_beginners_prompt)
    return str(best_for_beginners)
