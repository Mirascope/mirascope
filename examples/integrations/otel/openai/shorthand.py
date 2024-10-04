from mirascope.core import openai
from mirascope.integrations.otel import configure, with_otel

configure()


@with_otel()
@openai.call("gpt-4o-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book."


print(recommend_book("fantasy"))
