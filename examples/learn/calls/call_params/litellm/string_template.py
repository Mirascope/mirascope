from mirascope.core import litellm, prompt_template


@litellm.call("gpt-4o-mini", call_params={"max_tokens": 512})
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


response = recommend_book("fantasy")
print(response.content)
