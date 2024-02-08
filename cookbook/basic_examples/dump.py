"""A basic example on how to dump the data from a prompt and a chat completion."""
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
print("Prompt class data:")
print(prompt.dump())
completion = model.create(prompt)
print("ChatCompletion data:")
print(completion.dump())
print("Prompt and ChatCompletion data:")
print(prompt.dump(completion))
