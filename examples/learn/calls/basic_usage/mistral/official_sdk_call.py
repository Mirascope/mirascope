from mistralai import Mistral
import os

client = Mistral(api_key=os.environ.get("MISTRAL_API_KEY", ""))


def recommend_book(genre: str) -> str:
    completion = client.chat(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": f"Recommend a {genre} book"}],
    )
    return completion.choices[0].message.content


output = recommend_book("fantasy")
print(output)
