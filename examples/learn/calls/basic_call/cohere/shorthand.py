from mirascope.core import cohere


@cohere.call("command-r-plus")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


print(recommend_book("fantasy"))
