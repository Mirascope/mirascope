from mirascope.core import gemini
from pydantic import BaseModel, ConfigDict, Field


class Book(BaseModel):
    title: str = Field(..., examples=["THE NAME OF THE WIND"])
    author: str = Field(..., examples=["Rothfuss, Patrick"])

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"title": "THE NAME OF THE WIND", "author": "Rothfuss, Patrick"}
            ]
        }
    )


@gemini.call("gemini-1.5-flash", response_model=Book, json_mode=True)
def extract_book(text: str) -> str:
    return f"Extract {text}. Match examples format."


book = extract_book("The Way of Kings by Brandon Sanderson")
print(book)
# Output: title='THE NAME OF THE WIND' author='Rothfuss, Patrick'
