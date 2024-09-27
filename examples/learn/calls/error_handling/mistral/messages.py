from mirascope.core import Messages, mistral
from mistralai import models


@mistral.call("mistral-large-latest")
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


try:
    response = recommend_book("fantasy")
    print(response.content)
except models.HTTPValidationError as e:  # pyright: ignore [reportAttributeAccessIssue]
    # handle e.data: models.HTTPValidationErrorData
    raise (e)
except models.SDKError as e:  # pyright: ignore [reportAttributeAccessIssue]
    # handle exception
    raise (e)
