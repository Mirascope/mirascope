from mirascope.core import cohere


@cohere.call("command-r-plus")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


response: cohere.CohereCallResponse = recommend_book("fantasy")
print(response.content)
