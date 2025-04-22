from mirascope.core import prompt_template, xai
from mirascope.integrations.otel import configure, with_otel

configure()


@with_otel()
@xai.call("grok-3-mini")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
