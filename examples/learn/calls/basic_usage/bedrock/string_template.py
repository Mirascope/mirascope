from mirascope.core import bedrock, prompt_template


@bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


response = recommend_book("fantasy")
print(response.content)
