"""A basic prompt for recommending books on a topic"""
import os

from mirascope.openai import OpenAIPrompt

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


class BookRecommendationPrompt(OpenAIPrompt):
    """
    Can you recommend some books on {topic}?
    """

    topic: str


prompt = BookRecommendationPrompt(topic="how to bake a cake")
res = prompt.create()
print(str(res))
