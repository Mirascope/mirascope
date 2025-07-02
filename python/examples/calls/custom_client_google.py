from mirascope import llm

custom_client = llm.models.GoogleClient()


@llm.call(
    "google:gemini-2.5-flash",
    client=custom_client,
)
def recommend_book(genre: str):
    return f"Recommend a {genre} book"


response: llm.Response = recommend_book("fantasy")
print(response.text)
# "Here are a few highly recommended fantasy books..."
