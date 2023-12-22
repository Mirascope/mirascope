"""A basic prompt for recommending books on {topic}"""
import os

from mirascope import MirascopeChatOpenAI, MirascopePrompt


class BookRecommendationPrompt(MirascopePrompt):
    """
    Can you recommend some books on {topic}?
    """

    topic: str


prompt = BookRecommendationPrompt(topic="how to bake a cake")
model = MirascopeChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
res = model.create(prompt)
