"""A multi-chain prompt for recommending books on a {topic} and then asking which one 
is the best for beginners.
"""
import os

from mirascope import OpenAIChat, Prompt


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
    model = OpenAIChat(api_key=os.getenv("OPENAI_API_KEY"))
    book_recommendation_prompt = BookRecommendationPrompt(topic=topic)
    book_list = model.create(book_recommendation_prompt)

    best_for_beginners_prompt = BestForBeginnersPrompt(book_list=str(book_list))
    best_for_beginners = model.create(best_for_beginners_prompt)
    return str(best_for_beginners)


generate_best_book_for_beginners("how to bake a cake")
