from mirascope.core import mistral
from mistralai.models.chat_completion import ChatMessage


@mistral.call("mistral-large-latest")
def recommend_book(genre: str) -> mistral.MistralDynamicConfig:
    return {"messages": [ChatMessage(role="user", content=f"Recommend a {genre} book")]}


response = recommend_book("fantasy")
print(response.content)
