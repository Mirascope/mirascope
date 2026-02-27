from mirascope import llm


@llm.retry()
@llm.call("openai/gpt-4o-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response = recommend_book("fantasy")
print(response.text())
# > The Name of the Wind by Patrick Rothfuss
