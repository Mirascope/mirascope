from mirascope.core import anthropic, prompt_template


@anthropic.call("claude-3-5-sonnet-20240620", call_params={"max_tokens": 512})
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


response = recommend_book("fantasy")
print(response.content)
