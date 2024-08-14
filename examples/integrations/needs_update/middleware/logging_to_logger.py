"""Logging your LLM responses to the logger"""

import logging
import os

from mirascope.core import openai

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"

logger = logging.getLogger("mirascope")


os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY"


@openai.call(model="gpt-4o")
def recommend_books(topic: str):
    """Can you recommend some books on {topic}?"""


response = recommend_books(topic="how to bake a cake")
logger.info(response.model_dump())
