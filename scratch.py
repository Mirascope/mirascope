from mirascope.core import openai, prompt_template


@openai.call(model="gpt-4o-mini")
@prompt_template("Recommend a {genre} book.")
def recommend_book(genre: str): ...


response = recommend_book(genre="fantasy")
print(response.model_dump())
