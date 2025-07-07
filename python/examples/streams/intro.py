from mirascope import llm


@llm.call("openai:gpt-4o-mini")
def recommend_book(genre: str):
    return f"Recommend a {genre} book"


stream: llm.Stream = recommend_book.stream("fantasy")  # [!code highlight]
for content in stream:  # [!code highlight]
    if content.type == "text_chunk":  # [!code highlight]
        print(content.delta, end="", flush=True)  # [!code highlight]
