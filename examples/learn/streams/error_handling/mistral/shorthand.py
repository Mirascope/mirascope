from mirascope.core import mistral
from mistralai import models


@mistral.call("mistral-large-latest", stream=True)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


try:
    for chunk, _ in recommend_book("fantasy"):
        print(chunk.content, end="", flush=True)
except models.HTTPValidationError as e:  # pyright: ignore [reportAttributeAccessIssue]
    # handle e.data: models.HTTPValidationErrorData
    raise (e)
except models.SDKError as e:  # pyright: ignore [reportAttributeAccessIssue]
    # handle exception
    raise (e)
