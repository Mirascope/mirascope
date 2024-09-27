from mirascope.core import prompt_template, vertex


@vertex.call("gemini-1.5-flash", stream=True)
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


try:
    for chunk, _ in recommend_book("fantasy"):
        print(chunk.content, end="", flush=True)
except Exception as e:
    print(f"Error: {str(e)}")
