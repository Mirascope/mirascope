from typing import cast

from mirascope.core import mistral
from mistralai import Mistral

client = Mistral(api_key=mistral.load_api_key())


def recommend_book(genre: str) -> str | None:
    completion = client.chat.complete(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": f"Recommend a {genre} book"}],
    )
    if completion and (choices := completion.choices):
        return cast(str, choices[0].message.content)


output = recommend_book("fantasy")
print(output)
