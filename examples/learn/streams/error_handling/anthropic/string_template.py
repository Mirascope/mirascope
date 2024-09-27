from anthropic import AnthropicError
from mirascope.core import anthropic, prompt_template


@anthropic.call("claude-3-5-sonnet-20240620", stream=True)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


try:
    for chunk, _ in recommend_book("fantasy"):
        print(chunk.content, end="", flush=True)
except AnthropicError as e:
    print(f"Error: {str(e)}")
