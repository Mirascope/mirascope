from anthropic import AnthropicError # [!code highlight]
from mirascope.core import Messages, anthropic


@anthropic.call("claude-3-5-sonnet-20240620", stream=True)
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


try: # [!code highlight]
    for chunk, _ in recommend_book("fantasy"):
        print(chunk.content, end="", flush=True)
except AnthropicError as e: # [!code highlight]
    print(f"Error: {str(e)}")
