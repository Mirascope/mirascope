from mirascope.core import openai


@openai.call("gpt-4o-mini", call_params={"max_tokens": 512})
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response = recommend_book("fantasy")
print(response.content)
