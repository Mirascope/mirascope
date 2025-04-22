from openai import OpenAI

client = OpenAI(base_url="https://api.x.ai/v1", api_key="YOUR_KEY_HERE")


def recommend_book(genre: str) -> str:
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Recommend a {genre} book"}],
    )
    return str(completion.choices[0].message.content)


output = recommend_book("fantasy")
print(output)
