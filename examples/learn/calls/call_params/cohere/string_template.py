from mirascope.core import cohere, prompt_template


@cohere.call("command-r-plus", call_params={"max_tokens": 512})
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


response = recommend_book("fantasy")
print(response.content)
