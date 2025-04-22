from mirascope.core import google, prompt_template
from mirascope.integrations.otel import configure, with_otel

configure()


@with_otel()
@google.call("gemini-2.0-flash-001")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
