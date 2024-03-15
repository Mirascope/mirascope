"""
Basic example using an OpenAICall to stream a call
"""
import os

from mirascope.openai import OpenAICall

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


class BookRecommender(OpenAICall):
    prompt_template = "Please recommend a {genre} book."

    genre: str


stream = BookRecommender(genre="fantasy").stream()
for chunk in stream:
    print(chunk.content, end="")
# > The Name of the Wind by Patrick Rothfuss
