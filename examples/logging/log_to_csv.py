"""
Logging your LLM responses to a CSV file
"""
import os

import pandas as pd

from mirascope import tags
from mirascope.openai import OpenAICall

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


@tags(["recommendation_project"])
class BookRecommender(OpenAICall):
    prompt_template = """
    Can you recommend some books on {topic}?
    """

    topic: str


recommender = BookRecommender(topic="how to bake a cake")
response = recommender.call()
recommender_response_dump = recommender.dump() | response.dump()
df = pd.DataFrame([recommender_response_dump])
with open("log.csv", "w") as f:
    df.to_csv(f, index=False)
