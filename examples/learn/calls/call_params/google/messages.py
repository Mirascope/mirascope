from mirascope.core import Messages, google


@google.call(
    "gemini-1.5-flash",
    call_params={"config": {"max_output_tokens": 512}},
)
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


response = recommend_book("fantasy")
print(response.content)
