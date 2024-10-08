from mirascope.core import Messages, groq


@groq.call("llama-3.1-70b-versatile", call_params={"max_tokens": 512})
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


response = recommend_book("fantasy")
print(response.content)
