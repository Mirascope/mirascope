import json

from mirascope.core import groq, prompt_template


@groq.call("llama-3.1-8b-instant", json_mode=True)
@prompt_template("Provide the author and genre of {book_title}")
def get_book_info(book_title: str): ...


try:
    response = get_book_info("The Name of the Wind")
    print(json.loads(response.content))
except json.JSONDecodeError:
    print("The model produced invalid JSON")