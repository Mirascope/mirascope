from mirascope.core import mistral, prompt_template
from mirascope.integrations.otel import configure, with_otel

configure()


@with_otel()
@mistral.call("mistral-large-latest")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
