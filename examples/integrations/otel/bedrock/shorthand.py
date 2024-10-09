from mirascope.core import bedrock
from mirascope.integrations.otel import configure, with_otel

configure()


@with_otel()
@bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book."


print(recommend_book("fantasy"))
