from mirascope import llm

custom_client = llm.clients.OpenAIClient()


@llm.call(
    "openai:gpt-4o-mini",
    client=custom_client,
)
def recommend_book(genre: str):
    return f"Recommend a {genre} book"


response: llm.BaseResponse = recommend_book("fantasy")
print(response.text)
# "Here are a few highly recommended fantasy books..."
