from mirascope.core import gemini, prompt_template


@gemini.call("gemini-1.5-flash")
@prompt_template()
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


print(recommend_book("fantasy"))
