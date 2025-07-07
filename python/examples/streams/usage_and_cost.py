from mirascope import llm


@llm.call("openai:gpt-4o-mini")
def recommend_book(genre: str):
    return f"Recommend a {genre} book and explain why it's great."


stream = recommend_book.stream("fantasy")

for content in stream:
    print(content, end="", flush=True)
print("")  # Add trailing newline now that stream is complete

print(f"Final usage: {stream.usage}")  # [!code highlight]
print(f"Final cost: ${stream.cost}")  # [!code highlight]
