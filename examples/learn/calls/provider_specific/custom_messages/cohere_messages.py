from cohere.types.chat_message import ChatMessage
from mirascope.core import cohere


@cohere.call("command-r-plus")
def recommend_book(genre: str) -> cohere.CohereDynamicConfig:
    return {"messages": [ChatMessage(role="user", message=f"Recommend a {genre} book")]}  # pyright: ignore [reportCallIssue, reportReturnType]


response: cohere.CohereCallResponse = recommend_book("fantasy")
print(response.content)
