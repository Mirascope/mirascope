"""Logging your LLM responses to a CSV file"""
import os

import pandas as pd
from dotenv import load_dotenv

from mirascope.core.openai import openai_call

os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY"


@openai_call(model="gpt-4o")
def recommend_books(topic: str):
    """Can you recommend some books on {topic}?"""


response = recommend_books(topic="how to bake a cake")
df = pd.DataFrame([response.model_dump()])
with open("log.csv", "w") as f:
    df.to_csv(f, index=False)
