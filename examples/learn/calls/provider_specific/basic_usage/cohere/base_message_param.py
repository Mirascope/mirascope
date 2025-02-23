from mirascope.core import BaseMessageParam, cohere


@cohere.call("command-r-plus")
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


response: cohere.CohereCallResponse = recommend_book("fantasy")
print(response.content)
