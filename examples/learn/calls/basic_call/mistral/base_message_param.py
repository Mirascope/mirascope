from mirascope.core import BaseMessageParam, mistral


@mistral.call("mistral-large-latest")
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


print(recommend_book("fantasy"))
