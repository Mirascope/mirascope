from mirascope.core import mistral, prompt_template
from mistralai import models


@mistral.call("mistral-large-latest")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


try:
    response = recommend_book("fantasy")
    print(response.content)
except models.HTTPValidationError as e:  # pyright: ignore [reportAttributeAccessIssue]
    # handle e.data: models.HTTPValidationErrorData
    raise (e)
except models.SDKError as e:  # pyright: ignore [reportAttributeAccessIssue]
    # handle exception
    raise (e)
