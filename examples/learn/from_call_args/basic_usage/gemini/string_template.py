from typing import Annotated
from pydantic import BaseModel, Field
from mirascope.core import gemini, prompt_template, FromCallArgs


class BookRecommendation(BaseModel):
    genre: Annotated[str, FromCallArgs()]
    title: str = Field(..., description="The title of the recommended book")
    author: str = Field(..., description="The author of the recommended book")


@gemini.call("gemini-1.5-flash", response_model=BookRecommendation)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


print(recommend_book("fantasy"))
# Output: genre='fantasy' title='The Name of the Wind' author='Patrick Rothfuss'
