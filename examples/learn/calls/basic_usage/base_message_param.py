from mirascope import BaseMessageParam, llm


@llm.call(provider="openai", model="gpt-4o-mini")
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


response: llm.CallResponse = recommend_book("fantasy")
print(response.content)
