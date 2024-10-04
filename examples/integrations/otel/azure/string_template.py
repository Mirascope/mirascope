from mirascope.core import azure, prompt_template
from mirascope.integrations.otel import configure, with_otel

configure()


@with_otel()
@azure.call("gpt-4o-mini")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
