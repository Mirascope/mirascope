"""A multi-chain prompt example.

First, recommend books on a topic. Then, ask which one is the best for beginners.
"""
import os

from mirascope import OpenAIChat, Prompt

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


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


def generate_best_book_for_beginners(topic: str) -> str:
    """Generates the best book for beginners on the given topic."""
    model = OpenAIChat()
    book_recommendation_prompt = BookRecommendationPrompt(topic=topic)
    book_list = model.create(book_recommendation_prompt)

    best_for_beginners_prompt = BestForBeginnersPrompt(book_list=str(book_list))
    best_for_beginners = model.create(best_for_beginners_prompt)
    return str(best_for_beginners)


print(generate_best_book_for_beginners("how to bake a cake"))
