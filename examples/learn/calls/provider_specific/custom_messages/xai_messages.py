from mirascope.core import xai


@xai.call("grok-3")
def recommend_book(genre: str) -> xai.XAIDynamicConfig:
    return {"messages": [{"role": "user", "content": f"Recommend a {genre} book"}]}


response: xai.XAICallResponse = recommend_book("fantasy")
print(response.content)
