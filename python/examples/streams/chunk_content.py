from mirascope import llm


@llm.call("openai:gpt-4o-mini")
def recommend_book(genre: str):
    return f"Recommend a {genre} book and explain why it's great."


stream = recommend_book.stream("fantasy")

for chunk in stream:
    print(f"Raw content: {chunk.content}")

    if chunk.text:  # [!code highlight]
        print(f"Text: {chunk.text}")

    if chunk.image:  # [!code highlight]
        print(f"Image: {chunk.image}")

    if chunk.audio:  # [!code highlight]
        print(f"Audio: {chunk.audio}")

    if chunk.video:  # [!code highlight]
        print(f"Video: {chunk.video}")

    if chunk.thinking:  # [!code highlight]
        print(f"Thinking: {chunk.thinking}")

    if chunk.tool:  # [!code highlight]
        print(f"Tool invocation: {chunk.tool}")

    chunk_repr = str(chunk)
    print(f"Chunk representation: {chunk_repr}")
