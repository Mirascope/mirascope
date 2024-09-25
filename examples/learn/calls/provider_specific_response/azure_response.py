from mirascope.core import azure


@azure.call("gpt-4o-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response = recommend_book("fantasy")
# Type: ChatCompletions
original_response = response.response
