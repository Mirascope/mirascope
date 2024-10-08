from mirascope.core import azure, prompt_template


@azure.call("gpt-4o-mini", call_params={"max_tokens": 512})
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


response = recommend_book("fantasy")
print(response.content)
