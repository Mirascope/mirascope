from mirascope.core import azure, prompt_template


@azure.call("gpt-4o-mini")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


try:
    response = recommend_book("fantasy")
    print(response.content)
except Exception as e:
    print(f"Error: {str(e)}")
