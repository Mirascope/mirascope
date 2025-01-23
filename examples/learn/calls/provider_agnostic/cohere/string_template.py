from mirascope.core import prompt_template
from mirascope import llm


@llm.call(provider="cohere", model="command-r-plus")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


response = recommend_book("fantasy")
print(response.content)

override_response = llm.override(
    recommend_book,
    provider="anthropic",
    model="claude-3-5-sonnet-20240620",
    call_params={"temperature": 0.7},
)("fantasy")

print(override_response.content)
