from mirascope.core import BaseMessageParam, google


@google.call("gemini-2.0-flash")
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


response: google.GoogleCallResponse = recommend_book("fantasy")
print(response.content)
