from mirascope import llm


@llm.call(provider="anthropic", model="claude-3-5-sonnet-20240620")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response = recommend_book("fantasy")
print(response.content)

override_response = llm.override(
    recommend_book,
    provider_override="openai",
    model_override="gpt-4o-mini",
    call_params_override={"temperature": 0.7},
)("fantasy")

print(override_response.content)
