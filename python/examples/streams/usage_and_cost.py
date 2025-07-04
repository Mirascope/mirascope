from mirascope import llm


@llm.call("openai:gpt-4o-mini")
def recommend_book(genre: str):
    return f"Recommend a {genre} book and explain why it's great."


stream = recommend_book.stream("fantasy")

for chunk in stream:
    print(chunk.content, end="", flush=True)

    if chunk.usage:  # [!code highlight]
        print(f"\n[Chunk] Usage: {chunk.usage}")
    if chunk.cost:  # [!code highlight]
        print(f"[Chunk] Cost: ${chunk.cost}")

print(f"\nFinal usage: {stream.usage}")  # [!code highlight]
print(f"Final cost: ${stream.cost}")  # [!code highlight]
