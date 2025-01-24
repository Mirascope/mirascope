from mirascope.core import BaseMessageParam, google


@google.call(
    "gemini-1.5-flash",
    call_params={"config": {"max_output_tokens": 512}},
)
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


response = recommend_book("fantasy")
print(response.content)
