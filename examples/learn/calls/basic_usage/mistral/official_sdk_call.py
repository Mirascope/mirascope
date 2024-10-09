from mistralai.client import MistralClient

client = MistralClient()


def recommend_book(genre: str) -> str:
    completion = client.chat(
        model="mistral-large-latest",
        messages=[{"role": "user", "content": f"Recommend a {genre} book"}],
    )
    return completion.choices[0].message.content


output = recommend_book("fantasy")
print(output)
