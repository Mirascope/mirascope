from mirascope.core import prompt_template
from mirascope import llm


@llm.call(provider="bedrock", model="anthropic.claude-3-haiku-20240307-v1:0")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


response = recommend_book("fantasy")
print(response.content)

override_response = llm.override(
    recommend_book,
    provider_override="anthropic",
    model_override="claude-3-5-sonnet-20240620",
    call_params_override={"temperature": 0.7},
)("fantasy")

print(override_response.content)
