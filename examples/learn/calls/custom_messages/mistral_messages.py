from mirascope.core import mistral
from mistralai.models import UserMessage


@mistral.call("mistral-large-latest")
def recommend_book(genre: str) -> mistral.MistralDynamicConfig:
    return {"messages": [UserMessage(role="user", content=f"Recommend a {genre} book")]}


response: mistral.MistralCallResponse = recommend_book("fantasy")
print(response.content)
