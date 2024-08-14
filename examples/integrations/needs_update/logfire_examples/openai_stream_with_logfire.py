"""Basic example using an @openai.call to stream a call with logfire."""

import os

import logfire

from mirascope.core import openai
from mirascope.integrations.logfire import with_logfire

logfire.configure()

os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY"


@with_logfire
@openai.call(model="gpt-3.5-turbo", stream=True)
def recommend_book(genre: str):
    """Recommend a {genre} book."""


content = []
for chunk, tool in recommend_book(genre="fiction"):
    print(chunk.content, end="", flush=True)
