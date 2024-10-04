from typing import Annotated
from pydantic import BaseModel, Field
from mirascope.core import BaseMessageParam, vertex, FromCallArgs


class BookRecommendation(BaseModel):
    genre: Annotated[str, FromCallArgs()]
    title: str = Field(..., description="The title of the recommended book")
    author: str = Field(..., description="The author of the recommended book")


@vertex.call("gemini-1.5-flash", response_model=BookRecommendation)
def recommend_book(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


print(recommend_book("fantasy"))
# Output: genre='fantasy' title='The Name of the Wind' author='Patrick Rothfuss'
