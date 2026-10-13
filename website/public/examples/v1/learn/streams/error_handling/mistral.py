from mirascope.core import Messages, mistral # [!code highlight]
from mistralai import models


@mistral.call("mistral-large-latest", stream=True)
def recommend_book(genre: str) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book")


try: # [!code highlight]
    for chunk, _ in recommend_book("fantasy"):
        print(chunk.content, end="", flush=True)
except models.HTTPValidationError as e:  # pyright: ignore [reportAttributeAccessIssue] # [!code highlight]
    # handle e.data: models.HTTPValidationErrorData
    raise (e)
except models.SDKError as e:  # pyright: ignore [reportAttributeAccessIssue] # [!code highlight]
    # handle exception
    raise (e)
