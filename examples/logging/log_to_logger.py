"""
Logging your LLM responses to the logger
"""

import logging
import os

from mirascope import tags
from mirascope.openai import OpenAICall

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"

logger = logging.getLogger("mirascope")


@tags(["recommendation_project"])
class BookRecommender(OpenAICall):
    prompt_template = """
    Can you recommend some books on {topic}?
    """

    topic: str


recommender = BookRecommender(topic="how to bake a cake")
response = recommender.call()
recommender_response_dump = recommender.dump() | response.dump()
logger.info(recommender_response_dump)
