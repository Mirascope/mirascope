from mirascope import llm


@llm.call("openai/gpt-5-mini")
def recommend_book(genre: str):
    return f"Recommend a {genre} book."


response = recommend_book.stream("fantasy")
for chunk in response.chunk_stream():
    match chunk.type:
        case "text_chunk":
            print(chunk.delta, end="", flush=True)
        case _:
            pass
print()
