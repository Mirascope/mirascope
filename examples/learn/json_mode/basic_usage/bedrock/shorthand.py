import json

from mirascope.core import bedrock


@bedrock.call("anthropic.claude-3-haiku-20240307-v1:0", json_mode=True)
def get_book_info(book_title: str) -> str:
    return f"Provide the author and genre of {book_title}"


response = get_book_info("The Name of the Wind")
print(json.loads(response.content))
# Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
