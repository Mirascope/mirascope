from mirascope.core import mistral
from mistralai import Mistral

client = Mistral(api_key=mistral.load_api_key())


def recommend_book(genre: str) -> str:
    completion = client.chat(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": f"Recommend a {genre} book"}],
    )
    return completion.choices[0].message.content


output = recommend_book("fantasy")
print(output)
