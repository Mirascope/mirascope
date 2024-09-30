from litellm.exceptions import BadRequestError
from mirascope.core import BaseMessageParam, litellm


@litellm.call("gpt-4o-mini")
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


try:
    response = recommend_book("fantasy")
    print(response.content)
except BadRequestError as e:
    print(f"Error: {str(e)}")