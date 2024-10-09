from mirascope.core import gemini


@gemini.call("gemini-1.5-flash")
def recommend_book(genre: str) -> gemini.GeminiDynamicConfig:
    return {"messages": [{"role": "user", "parts": [f"Recommend a {genre} book"]}]}


response = recommend_book("fantasy")
print(response.content)
