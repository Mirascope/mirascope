from mirascope.core import openai, prompt_template


def format_book(title: str, author: str) -> str:
    """Format a book's title and author."""
    return f"{title} by {author}"


@openai.call(model="gpt-4", tools=[format_book], stream=True)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


for chunk, tool in recommend_book("fantasy"):
    if tool:
        print(tool.call())
    else:
        print(chunk.content, end="", flush=True)
