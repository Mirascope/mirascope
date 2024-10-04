from mirascope.core import cohere, prompt_template
from mirascope.integrations.otel import configure, with_otel

configure()


@with_otel()
@cohere.call("command-r-plus")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
