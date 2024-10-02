from cohere.errors import BadRequestError
from mirascope.core import cohere


@cohere.call(model="command-r-plus")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


try:
    response = recommend_book("fantasy")
    print(response.content)
except BadRequestError as e:
    print(f"Error: {str(e)}")
