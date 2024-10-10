from mirascope.core import bedrock, prompt_template
from mirascope.integrations.otel import configure, with_otel

configure()


@with_otel()
@bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
