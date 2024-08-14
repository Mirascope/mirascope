"""Basic example using an @openai.call to stream a call with OpenTelemetry."""

import os

from mirascope.core import openai
from mirascope.integrations.otel import with_otel

os.environ["OPENAI_API_KEY"] = "sk-YOUR_OPENAI_API_KEY"


@with_otel
@openai.call(model="gpt-3.5-turbo", stream=True)
def recommend_book(genre: str):
    """Recommend a {genre} book."""


results = recommend_book(genre="fiction")
for chunk, _ in results:
    print(chunk.content, flush=True, end="")
