import os
from typing import cast

from mistralai import Mistral

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])


def recommend_book(genre: str) -> str | None:
    completion = client.chat.complete(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": f"Recommend a {genre} book"}],
    )
    if completion and (choices := completion.choices):
        return cast(str, choices[0].message.content)


output = recommend_book("fantasy")
print(output)
