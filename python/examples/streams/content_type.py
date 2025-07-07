from mirascope import llm


@llm.call("openai:gpt-4o-mini")
def recommend_book(genre: str):
    return f"Recommend a {genre} book, and provide image and audio references."


stream = recommend_book.stream("fantasy")

for content in stream:
    if content.type == "text_chunk":  # [!code highlight]
        print(f"TextChunk with delta: {content.delta}")
    elif content.type == "image_partial":  # [!code highlight]
        print("ImagePartial")
    elif content.type == "audio_chunk":  # [!code highlight]
        print("AudioChunk")
    elif content.type == "thinking_chunk":  # [!code highlight]
        print(f"Thinking chunk with delta: {content.delta}")
    elif content.type == "tool_call_chunk":  # [!code highlight]
        print(f"ToolCallChunk name: {content.name}, args delta: {content.delta}")
