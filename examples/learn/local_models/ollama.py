from mirascope.core import openai
from pydantic import BaseModel
from openai import OpenAI


# Follow the link to see what features of openai are supported
# https://github.com/ollama/ollama/blob/main/docs/openai.md
custom_client = OpenAI(
    base_url="http://localhost:11434/v1",  # your ollama endpoint
    api_key="unused",  # required by openai, but unused
)

class Book(BaseModel):
    title: str
    author: str

@openai.call("llama3.2", client=custom_client)
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"

@openai.call("llama3.2", response_model=Book, client=custom_client)
def extract_book(text: str) -> str:
    return f"Extract {text}"


# --------------
# call the function as you do with any other integration
recommendation = recommend_book("fantasy")

print(recommendation)
# Output: Here are some popular and highly-recommended fantasy books...

# --------------
# function calling works as well!
book = extract_book("The Name of the Wind by Patrick Rothfuss")

assert isinstance(book, Book)
print(book)
# Output: title='The Name of the Wind' author='Patrick Rothfuss'
