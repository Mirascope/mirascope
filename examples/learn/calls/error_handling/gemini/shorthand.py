from mirascope.core import gemini


@gemini.call(model="gemini-1.5-flash")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


try:
    response = recommend_book("fantasy")
    print(response.content)
except Exception as e:
    print(f"Error: {str(e)}")
