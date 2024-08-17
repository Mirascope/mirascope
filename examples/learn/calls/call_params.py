from mirascope.core import openai, prompt_template


@openai.call("gpt-4o-mini", call_params={"temperature": 0.7})
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


response = recommend_book("fantasy")
print(response.content)
