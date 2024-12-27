from mirascope.core import prompt_template
from mirascope import llm


@llm.call(provider="azure", model="gpt-4o-mini")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


response = recommend_book("fantasy")
print(response.content)
