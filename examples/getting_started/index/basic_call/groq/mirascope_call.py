from mirascope.core import groq, prompt_template


@groq.call("llama-3.1-8b-instant")
@prompt_template()
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


print(recommend_book("fantasy"))
