import json

from mirascope.core import openai, prompt_template


@openai.call(model="gpt-4o-mini", json_mode=True)
@prompt_template(
    """
    Provide the following information about {book_title}:
    - author
    - date published
    - genre
    """
)
def get_book_info(book_title: str): ...


try:
    response = get_book_info("The Great Gatsby")
    json_obj = json.loads(response.content)
    print(json_obj["author"])
except json.JSONDecodeError:
    print("The model produced invalid JSON")
