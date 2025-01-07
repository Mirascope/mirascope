from mirascope.core import Messages
from mirascope import llm


@llm.call(provider="gemini", model="gemini-1.5-flash")
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


response = recommend_book("fantasy")
print(response.content)

override_response = llm.override(
    recommend_book,
    provider_override="anthropic",
    model_override="claude-3-5-sonnet-20240620",
    call_params_override={"temperature": 0.7},
)("fantasy")

print(override_response.content)
