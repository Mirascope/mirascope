from mirascope import llm, prompt_template
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


@llm.call(provider="openai", model="gpt-4o-mini", response_model=Book, json_mode=True)
@prompt_template("Extract {text}. Match example format EXCLUDING 'examples' key.")
def extract_book(text: str): ...


book = extract_book("The Way of Kings by Brandon Sanderson")
print(book)
# Output: title='THE WAY OF KINGS' author='Sanderson, Brandon'
