from google.genai import Client

client = Client()


def recommend_book(genre: str) -> str:
    generation = client.models.generate_content(
        model="gemini-2.0-flash",
        contents={"role": "user", "parts": [{"text": f"Recommend a {genre} book"}]},  # pyright: ignore [reportArgumentType]
    )
    return generation.candidates[0].content.parts[0].text  # pyright: ignore [reportOptionalSubscript, reportOptionalMemberAccess, reportReturnType]


output = recommend_book("fantasy")
print(output)
