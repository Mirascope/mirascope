from cohere.errors import BadRequestError
from mirascope.core import cohere, prompt_template


@cohere.call("command-r-plus", stream=True)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


try:
    for chunk, _ in recommend_book("fantasy"):
        print(chunk.content, end="", flush=True)
except BadRequestError as e:
    print(f"Error: {str(e)}")
