"""A FastAPI app integrated with a multi-chain prompt for recommending books on a topic 
and then asking which one is the best for beginners.

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
def root(book_recommendation: BookRecommendationPrompt):
    """Generates the best book for beginners on the given topic."""
    book_list = book_recommendation.create()

    best_for_beginners_prompt = BestForBeginnersPrompt(book_list=str(book_list))
    best_for_beginners = best_for_beginners_prompt.create()
    return str(best_for_beginners)
