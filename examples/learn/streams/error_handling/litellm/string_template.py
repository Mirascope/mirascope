from litellm.exceptions import BadRequestError
from mirascope.core import litellm, prompt_template


@litellm.call("gpt-4o-mini", stream=True)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


try:
    for chunk, _ in recommend_book("fantasy"):
        print(chunk.content, end="", flush=True)
except BadRequestError as e:
    print(f"Error: {str(e)}")
