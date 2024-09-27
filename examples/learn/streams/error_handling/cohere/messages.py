from cohere.errors import BadRequestError
from mirascope.core import Messages, cohere


@cohere.call("command-r-plus", stream=True)
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


try:
    for chunk, _ in recommend_book("fantasy"):
        print(chunk.content, end="", flush=True)
except BadRequestError as e:
    print(f"Error: {str(e)}")
