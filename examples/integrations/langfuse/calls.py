from mirascope.core import anthropic, prompt_template
from mirascope.integrations.langfuse import with_langfuse


def format_book(title: str, author: str):
    return f"{title} by {author}"


@with_langfuse()
@anthropic.call(model="claude-3-5-sonnet-20240620", tools=[format_book])
@prompt_template("Recommend a {genre} book.")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
