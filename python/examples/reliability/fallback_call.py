from mirascope import llm


@llm.retry(
    fallback_models=[
        "anthropic/claude-3-5-haiku-latest",
        "google/gemini-2.0-flash",
    ]
)
@llm.call("openai/gpt-4o-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response = recommend_book("fantasy")
print(response.text())
# > The Name of the Wind by Patrick Rothfuss
