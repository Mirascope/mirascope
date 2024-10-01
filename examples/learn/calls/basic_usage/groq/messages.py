from mirascope.core import Messages, groq


@groq.call("llama-3.1-8b-instant")
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


print(recommend_book("fantasy"))
