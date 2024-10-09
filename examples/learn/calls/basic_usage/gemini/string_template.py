from mirascope.core import gemini, prompt_template


@gemini.call("gemini-1.5-flash")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


response = recommend_book("fantasy")
print(response.content)
