from mirascope.core import Messages, openai
from openai import OpenAIError # [!code highlight]


@openai.call("gpt-4o-mini", stream=True)
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


try: # [!code highlight]
    for chunk, _ in recommend_book("fantasy"):
        print(chunk.content, end="", flush=True)
except OpenAIError as e: # [!code highlight]
    print(f"Error: {str(e)}")
