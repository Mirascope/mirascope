from litellm import completion


def recommend_book(genre: str) -> str:
    response = completion(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Recommend a {genre} book"}],
    )
    return str(response.choices[0].message.content)  # type: ignore


output = recommend_book("fantasy")
print(output)
