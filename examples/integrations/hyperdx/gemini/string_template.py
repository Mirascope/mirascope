from mirascope.core import gemini, prompt_template
from mirascope.integrations.otel import with_hyperdx


@with_hyperdx()
@gemini.call("gemini-1.5-flash")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
