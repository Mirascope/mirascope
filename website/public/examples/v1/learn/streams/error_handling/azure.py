from mirascope.core import azure # [!code highlight]


@azure.call(model="gpt-4o-mini", stream=True)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


try: # [!code highlight]
    for chunk, _ in recommend_book("fantasy"):
        print(chunk.content, end="", flush=True)
except Exception as e: # [!code highlight]
    print(f"Error: {str(e)}")
