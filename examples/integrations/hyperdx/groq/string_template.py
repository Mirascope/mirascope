from mirascope.core import groq, prompt_template
from mirascope.integrations.otel import with_hyperdx


@with_hyperdx()
@groq.call("llama-3.3-70b-versatile")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
