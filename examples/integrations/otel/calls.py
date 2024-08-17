from mirascope.core import anthropic, prompt_template
from mirascope.integrations.otel import configure, with_otel

configure()


def format_book(title: str, author: str) -> str:
    return f"{title} by {author}"


@with_otel()
@anthropic.call(model="claude-3-5-sonnet-20240620", tools=[format_book])
@prompt_template("Recommend a {genre} book.")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
