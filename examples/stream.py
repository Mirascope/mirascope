"""A basic prompt for streaming book recommendations on a topic"""
import os

from mirascope import OpenAIChat, Prompt

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


class BookRecommendationPrompt(Prompt):
    """
    Can you recommend some books on {topic}?
    """

    topic: str


def stream_book_recommendation(prompt: BookRecommendationPrompt):
    """Streams the response for a call to the model using `prompt`."""
    model = OpenAIChat()
    stream = model.stream(prompt)
    for chunk in stream:
        print(chunk, end="")


prompt = BookRecommendationPrompt(topic="how to bake a cake")
stream_book_recommendation(prompt)
