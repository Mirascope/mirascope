from mirascope import llm


@llm.call("openai:gpt-4o-mini")
def recommend_book(genre: str):
    return f"Recommend a {genre} book"


stream: llm.Stream = recommend_book.stream("fantasy")  # [!code highlight]
for chunk in stream:  # [!code highlight]
    print(chunk, end="", flush=True)  # [!code highlight]
