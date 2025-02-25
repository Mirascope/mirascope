from mirascope import llm


@llm.call(provider="openai", model="gpt-4o-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response: llm.CallResponse = recommend_book("fantasy")
print(response.content)

override_response = llm.override(
    recommend_book,
    provider="anthropic",
    model="claude-3-5-sonnet-latest",
    call_params={"temperature": 0.7},
)("fantasy")

print(override_response.content)
