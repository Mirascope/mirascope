from typing import Annotated
from pydantic import BaseModel, Field
from mirascope.core import groq, FromCallArgs


class BookRecommendation(BaseModel):
    genre: Annotated[str, FromCallArgs()]
    title: str = Field(..., description="The title of the recommended book")
    author: str = Field(..., description="The author of the recommended book")


@groq.call("llama-3.1-70b-versatile", response_model=BookRecommendation)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


print(recommend_book("fantasy"))
# Output: genre='fantasy' title='The Name of the Wind' author='Patrick Rothfuss'
