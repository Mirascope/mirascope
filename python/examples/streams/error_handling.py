from mirascope import llm


@llm.call("openai:gpt-4o-mini")
def recommend_book(genre: str):
    return f"Recommend a {genre} book and explain why it's great."


try:
    stream = recommend_book.stream("fantasy")

    for content in stream:
        print(content, end="", flush=True)

except llm.MirascopeError as e:
    print(f"\nStreaming error: {e}")

except Exception as e:
    print(f"\nUnexpected error: {e}")

else:
    print("\nStream completed successfully")
    print(f"Final usage: {stream.usage}")
    print(f"Final cost: ${stream.cost}")
