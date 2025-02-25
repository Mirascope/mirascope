from mirascope.core import litellm, prompt_template


@litellm.call("gpt-4o-mini")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


response: litellm.LiteLLMCallResponse = recommend_book("fantasy")
print(response.content)
