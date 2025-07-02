from mirascope import llm

custom_client = llm.models.AnthropicClient()


@llm.call(
    "anthropic:claude-3-5-sonnet-latest",
    client=custom_client,
)
def recommend_book(genre: str):
    return f"Recommend a {genre} book"


response: llm.Response = recommend_book("fantasy")
print(response.text)
# "Here are a few highly recommended fantasy books..."
