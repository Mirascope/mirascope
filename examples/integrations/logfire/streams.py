import logfire

from mirascope.core import openai, prompt_template
from mirascope.integrations.logfire import with_logfire

logfire.configure()


@with_logfire()
@openai.call(
    model="gpt-4o-mini",
    stream=True,
    call_params={"stream_options": {"include_usage": True}},
)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book."


for chunk, _ in recommend_book("fantasy"):
    print(chunk.content, end="", flush=True)
