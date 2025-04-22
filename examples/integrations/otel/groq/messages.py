from mirascope.core import Messages, groq
from mirascope.integrations.otel import configure, with_otel

configure()


@with_otel()
@groq.call("llama-3.3-70b-versatile")
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


print(recommend_book("fantasy"))
