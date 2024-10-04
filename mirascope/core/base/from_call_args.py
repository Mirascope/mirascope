from pydantic.fields import FieldInfo


class FromCallArgs:
    """Use this metadata to pass function arguments through to the response model.

    Example:

    ```python
    from typing import Annotated
    from pydantic import BaseModel, Field
    from mirascope.core import openai, prompt_template
    from mirascope.core.base import FromCallArgs

    class BookRecommendation(BaseModel):
        genre: Annotated[str, FromCallArgs()]
        title: str = Field(..., description="The title of the recommended book")
        author: str = Field(..., description="The author of the recommended book")
        description: str = Field(..., description="A brief description of the book, max 100 words")

    @openai.call(model="gpt-4o-mini", response_model=BookRecommendation)
    @prompt_template(
        '''
        You are an expert librarian with extensive knowledge of books across various genres.
        Recommend a {genre} book. Provide the title, author, and a brief description.
        '''
    )
    def recommend_book(genre: str): ...
    ```
    """

    pass


def is_from_call_args(field: FieldInfo) -> bool:
    return any(isinstance(m, FromCallArgs) for m in field.metadata)
