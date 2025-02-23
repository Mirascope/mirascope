from mirascope.core import BaseMessageParam, openai


@openai.call("gpt-4o-mini")
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


response: openai.OpenAICallResponse = recommend_book("fantasy")
print(response.content)
