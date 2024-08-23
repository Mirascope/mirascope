from mirascope.core import openai, prompt_template


def format_book(title: str, author: str) -> str:
    """Format a book's title and author."""
    return f"{title} by {author}"


@openai.call("gpt-4o-mini", tools=[format_book])  # OR `tools=[format_book]`
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


response = recommend_book("fantasy")
if tools := response.tools:
    for tool in tools:
        print(tool.call())
else:
    print(response.content)
