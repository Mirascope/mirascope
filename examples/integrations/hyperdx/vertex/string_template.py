from mirascope.core import prompt_template, vertex
from mirascope.integrations.otel import with_hyperdx


@with_hyperdx()
@vertex.call("gemini-1.5-flash")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
