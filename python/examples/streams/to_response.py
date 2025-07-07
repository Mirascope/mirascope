from mirascope import llm


@llm.call("openai:gpt-4o-mini")
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


stream: llm.Stream = recommend_book.stream("fantasy")

for content in stream:
    print(content, end="", flush=True)

response: llm.Response = stream.to_response()  # [!code highlight]
