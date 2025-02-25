from mirascope.core import anthropic, prompt_template


@anthropic.call("claude-3-5-sonnet-latest")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


response: anthropic.AnthropicCallResponse = recommend_book("fantasy")
print(response.content)
