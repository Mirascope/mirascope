from mirascope.core import cohere

# [!code highlight:4]
@cohere.call("command-r-plus")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response: cohere.CohereCallResponse = recommend_book("fantasy")
print(response.content)
