from mirascope.core import prompt_template
from mirascope.llm import call


@call(provider="cohere", model="command-r-plus")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


response = recommend_book("fantasy")
print(response.content)
