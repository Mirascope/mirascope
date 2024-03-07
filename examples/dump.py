"""A basic example on how to dump the data from a prompt and a chat completion."""
import os

from mirascope import tags
from mirascope.openai import OpenAIPrompt

os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"


@tags(["recommendation_project", "version:0001"])
class BookRecommendationPrompt(OpenAIPrompt):
    """
    Can you recommend some books on {topic}?
    """

    topic: str


prompt = BookRecommendationPrompt(topic="how to bake a cake")
print("Prompt class data:")
print(prompt.dump(), "\n")
completion = prompt.create()
print("ChatCompletion data:")
completion_data = completion.dump()
print(completion_data, "\n")
print("Prompt and ChatCompletion data:")
print(prompt.dump(completion_data))
