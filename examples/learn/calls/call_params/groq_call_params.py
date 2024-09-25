from mirascope.core import groq


@groq.call("llama-3.1-8b-instant", call_params={"max_tokens": 512})
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


print(recommend_book("fantasy"))
