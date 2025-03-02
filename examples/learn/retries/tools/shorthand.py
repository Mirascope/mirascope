from mirascope import llm
from tenacity import retry, stop_after_attempt, wait_exponential


def get_book_author(title: str) -> str:
    if title == "The Name of the Wind":
        return "Patrick Rothfuss"
    elif title == "Mistborn: The Final Empire":
        return "Brandon Sanderson"
    else:
        return "Unknown"


@llm.call(provider="openai", model="gpt-4o-mini", tools=[get_book_author])
def identify_author(book: str) -> str:
    return f"Who wrote {book}?"


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
)
def run():
    response = identify_author("The Name of the Wind")
    if tool := response.tool:
        print(tool.call())
        print(f"Original tool call: {tool.tool_call}")
    else:
        print(response.content)


run()
