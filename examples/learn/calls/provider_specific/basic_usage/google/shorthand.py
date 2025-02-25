from mirascope.core import google


@google.call("gemini-2.0-flash")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response: google.GoogleCallResponse = recommend_book("fantasy")
print(response.content)
