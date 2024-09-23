from mirascope.core import prompt_template, vertex


@vertex.call("gemini-1.5-flash", stream=True)
@prompt_template()
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


print(recommend_book("fantasy"))
