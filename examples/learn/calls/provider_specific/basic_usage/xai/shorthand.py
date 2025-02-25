from mirascope.core import xai


@xai.call("grok-3")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response: xai.XAICallResponse = recommend_book("fantasy")
print(response.content)
