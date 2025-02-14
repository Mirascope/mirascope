from mirascope.core import BaseMessageParam, google


@google.call("gemini-1.5-flash", stream=True)
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


try:
    for chunk, _ in recommend_book("fantasy"):
        print(chunk.content, end="", flush=True)
except Exception as e:
    print(f"Error: {str(e)}")
