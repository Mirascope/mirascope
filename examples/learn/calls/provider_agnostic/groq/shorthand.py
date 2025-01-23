from mirascope import llm


@llm.call(provider="groq", model="llama-3.1-70b-versatile")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response = recommend_book("fantasy")
print(response.content)

override_response = llm.override(
    recommend_book,
    provider="anthropic",
    model="claude-3-5-sonnet-20240620",
    call_params={"temperature": 0.7},
)("fantasy")

print(override_response.content)
