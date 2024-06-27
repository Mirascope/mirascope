"""Basic example using an @openai.call to make a call with logfire."""

import os

import logfire

from mirascope.core import openai
from mirascope.integrations.logfire import with_logfire

os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY"

logfire.configure()


@with_logfire
@openai.call(model="gpt-3.5-turbo")
def recommend_book(genre: str):
    """Recommend a {genre} book."""


results = recommend_book(genre="fiction")
print(results.content)
