from mirascope import llm


@llm.call("openai:gpt-4o-mini")
def recommend_book(genre: str):
    return f"Recommend a {genre} book and explain why it's great."


stream = recommend_book.stream("fantasy")

for content in stream:
    print(f"Raw content: {content}")

    if content.type == "text_chunk":  # [!code highlight]
        print(f"Text delta: {content.delta}")
        print(f"Text partial: {content.partial}")

    elif content.type == "image_chunk":  # [!code highlight]
        print(f"Image MIME type: {content.mime_type}")
        print(f"Image partial: {content.partial[:50]}...")  # Show first 50 chars

    elif content.type == "audio_chunk":  # [!code highlight]
        print(f"Audio MIME type: {content.mime_type}")
        print(f"Audio delta: {content.delta[:50]}...")  # Show first 50 chars

    elif content.type == "thinking_chunk":  # [!code highlight]
        print(f"Thinking delta: {content.delta}")
        print(f"Thinking partial: {content.partial}")

    elif content.type == "tool_call_chunk":  # [!code highlight]
        print(f"Tool name: {content.name}")
        print(f"Tool args delta: {content.args_delta}")
        print(f"Tool args partial: {content.args_partial}")

    content_repr = str(content)
    print(f"Content representation: {content_repr}")
