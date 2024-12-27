from mirascope.core import prompt_template
from mirascope import llm


@llm.call(provider="bedrock", model="anthropic.claude-3-haiku-20240307-v1:0")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


response = recommend_book("fantasy")
print(response.content)
