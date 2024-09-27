from litellm.exceptions import BadRequestError
from mirascope.core import Messages, litellm


@litellm.call("gpt-4o-mini")
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


try:
    response = recommend_book("fantasy")
    print(response.content)
except BadRequestError as e:
    print(f"Error: {str(e)}")
