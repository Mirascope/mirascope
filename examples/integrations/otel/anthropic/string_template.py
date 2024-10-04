from mirascope.core import anthropic, prompt_template
from mirascope.integrations.otel import configure, with_otel

configure()


@with_otel()
@anthropic.call("claude-3-5-sonnet-20240620")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
