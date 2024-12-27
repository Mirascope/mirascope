from mirascope.core import prompt_template
from mirascope.llm import call


@call(provider="groq", model="llama-3.1-70b-versatile")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


response = recommend_book("fantasy")
print(response.content)
