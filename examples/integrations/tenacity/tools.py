from tenacity import retry, stop_after_attempt, wait_exponential

from mirascope.core import anthropic, prompt_template


def format_book(title: str, author: str) -> str:
    return f"{title} by {author}"


@anthropic.call("claude-3-5-sonnet-20240620", tools=[format_book])
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
def run():
    response = recommend_book("fantasy")
    if tool := response.tool:
        print(tool.call())
    else:
        print(response.content)


run()
