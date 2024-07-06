"""Basic example using an @openai.call to make a call with langfuse."""

import os

from mirascope.core import openai
from mirascope.integrations.langfuse import with_langfuse

os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY"


@with_langfuse
@openai.call(model="gpt-3.5-turbo", stream=True)
def recommend_book(genre: str):
    """Recommend a {genre} book."""


for chunk, _ in recommend_book(genre="fiction"):
    print(chunk.content, end="", flush=True)
