"""
Basic example using an OpenAICall to make a call
"""

import os

from mirascope.openai import OpenAICall

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"


class BookRecommender(OpenAICall):
    prompt_template = "Please recommend a {genre} book."

    genre: str


response = BookRecommender(genre="fantasy").call()
print(response.content)
# > The Name of the Wind by Patrick Rothfuss
