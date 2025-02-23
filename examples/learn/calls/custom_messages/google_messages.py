from mirascope.core import Messages, google


@google.call("gemini-2.0-flash")
def recommend_book(genre: str) -> google.GoogleDynamicConfig:
    return {"messages": [Messages.User(f"Recommend a {genre} book")]}


response: google.GoogleCallResponse = recommend_book("fantasy")
print(response.content)
