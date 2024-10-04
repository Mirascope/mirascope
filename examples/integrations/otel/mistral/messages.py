from mirascope.core import Messages, mistral
from mirascope.integrations.otel import configure, with_otel

configure()


@with_otel()
@mistral.call("mistral-large-latest")
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


print(recommend_book("fantasy"))
