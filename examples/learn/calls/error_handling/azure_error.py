from mirascope.core import azure


@azure.call(model="gpt-4o-mini")
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


try:
    response = recommend_book("fantasy")
    print(response.content)
except Exception as e:
    print(f"Error: {str(e)}")
