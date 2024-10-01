import json

from mirascope.core import BaseMessageParam, openai


@openai.call("gpt-4o-mini", json_mode=True)
def get_book_info(book_title: str) -> list[BaseMessageParam]:
    return [
        BaseMessageParam(
            role="user", content=f"Provide the author and genre of {book_title}"
        )
    ]


response = get_book_info("The Name of the Wind")
print(json.loads(response.content))
# Output: {'author': 'Patrick Rothfuss', 'genre': 'Fantasy'}
