from mirascope.core import google


@google.call(
    "gemini-1.5-flash",
    call_params={"config": {"max_output_tokens": 512}},
)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response = recommend_book("fantasy")
print(response.content)
