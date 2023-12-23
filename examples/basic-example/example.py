"""A basic prompt for recommending books on a topic"""
import os

from mirascope import OpenAIChat, Prompt


class BookRecommendationPrompt(Prompt):
    """
    Can you recommend some books on {topic}?
    """

    topic: str


prompt = BookRecommendationPrompt(topic="how to bake a cake")
model = OpenAIChat(api_key=os.getenv("OPENAI_API_KEY"))
res = model.create(prompt)
print(str(res))
