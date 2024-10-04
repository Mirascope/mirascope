import logfire

from mirascope.core import anthropic
from mirascope.integrations.logfire import with_logfire

logfire.configure()


def format_book(title: str, author: str):
    return f"{title} by {author}"


@with_logfire()
@anthropic.call(model="claude-3-5-sonnet-20240620", tools=[format_book])
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book."


print(recommend_book("fantasy"))
