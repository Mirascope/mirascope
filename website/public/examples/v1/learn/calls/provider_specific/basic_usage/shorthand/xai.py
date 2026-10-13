from mirascope.core import xai

# [!code highlight:4]
@xai.call("grok-3")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response: xai.XAICallResponse = recommend_book("fantasy")
print(response.content)
