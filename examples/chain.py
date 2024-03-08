"""A multi-chain prompt example.

First, recommend books on a topic. Then, ask which one is the best for beginners.
"""
import os

from mirascope.openai import OpenAIPrompt

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


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


def generate_best_book_for_beginners(topic: str) -> str:
    """Generates the best book for beginners on the given topic."""
    book_recommendation_prompt = BookRecommendationPrompt(topic=topic)
    book_list = book_recommendation_prompt.create()

    best_for_beginners_prompt = BestForBeginnersPrompt(book_list=str(book_list))
    best_for_beginners = best_for_beginners_prompt.create()
    return str(best_for_beginners)


print(generate_best_book_for_beginners("how to bake a cake"))
