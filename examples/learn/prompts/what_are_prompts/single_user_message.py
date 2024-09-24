from openai import OpenAI

client = OpenAI()


def recommend_book(genre: str) -> str | None:
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"recommend a {genre} book"}],
    )
    return completion.choices[0].message.content
