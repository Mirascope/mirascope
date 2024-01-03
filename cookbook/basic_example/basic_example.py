"""A basic prompt for recommending books on a topic"""
import os

from mirascope import OpenAIChat, Prompt

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


class BookRecommendationPrompt(Prompt):
    """
    Can you recommend some books on {topic}?
    """

    topic: str


prompt = BookRecommendationPrompt(topic="how to bake a cake")
model = OpenAIChat()
res = model.create(prompt)
print(str(res))
