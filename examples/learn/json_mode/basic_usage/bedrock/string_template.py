import json

from mirascope.core import bedrock, prompt_template


@bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", json_mode=True)
@prompt_template("Provide the author and genre of {book_title}")
def get_book_info(book_title: str): ...


response = get_book_info("The Name of the Wind")
print(json.loads(response.content))
# Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
