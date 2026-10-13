from mirascope.core import xai
from openai import OpenAIError # [!code highlight]


@xai.call("grok-3-mini", stream=True)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


try: # [!code highlight]
    for chunk, _ in recommend_book("fantasy"):
        print(chunk.content, end="", flush=True)
except OpenAIError as e: # [!code highlight]
    print(f"Error: {str(e)}")
