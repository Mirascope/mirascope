from mirascope.core import Messages, mistral


@mistral.call("mistral-large-latest", call_params={"max_tokens": 512})
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


print(recommend_book("fantasy"))
