from mirascope.core import litellm, prompt_template
from mirascope.integrations.otel import with_hyperdx


@with_hyperdx()
@litellm.call("gpt-4o-mini")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
