"""A FastAPI app integrated with a multi-chain prompt for recommending books on a topic 
and then asking which one is the best for beginners.

How to Run:

    uvicorn api_example:app --reload
"""
import os

from fastapi import FastAPI

from mirascope import OpenAIChat, Prompt

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"

app = FastAPI()


class BookRecommendationPrompt(Prompt):
    """
    Can you recommend some books on {topic} in a list format?
    """

    topic: str


class BestForBeginnersPrompt(Prompt):
    """
    Given this list {book_list}, which one is the best for beginners?
    """

    book_list: str


@app.post("/")
def root(book_recommendation: BookRecommendationPrompt):
    """Generates the best book for beginners on the given topic."""
    model = OpenAIChat()
    book_list = model.create(book_recommendation)

    best_for_beginners_prompt = BestForBeginnersPrompt(book_list=str(book_list))
    best_for_beginners = model.create(best_for_beginners_prompt)
    return str(best_for_beginners)
