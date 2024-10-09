from vertexai.generative_models import GenerativeModel

client = GenerativeModel("gemini-1.5-flash")


def recommend_book(genre: str) -> str:
    generation = client.generate_content(
        contents=[{"role": "user", "parts": f"Recommend a {genre} book"}]
    )
    return generation.candidates[0].content.parts[0].text  # type: ignore


output = recommend_book("fantasy")
print(output)
