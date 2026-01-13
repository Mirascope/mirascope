from cohere.errors import BadRequestError # [!code highlight]
from mirascope.core import cohere


@cohere.call(model="command-r-plus", stream=True)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


try: # [!code highlight]
    for chunk, _ in recommend_book("fantasy"):
        print(chunk.content, end="", flush=True)
except BadRequestError as e: # [!code highlight]
    print(f"Error: {str(e)}")
