from mirascope import llm


@llm.call("openai:gpt-4o-mini")
def recommend_book(genre: str):
    return f"Recommend a {genre} book, and provide image and audio references."


stream = recommend_book.stream("fantasy")

for chunk in stream:
    print(f"Chunk type: {chunk.type}")
    # "ChunkStart", "ChunkEnd", "TextChunk", "ImageChunk", etc
    if chunk.type != "chunk_start" and chunk.type != "chunk_end":
        print(chunk.delta)
    if chunk.type == "audio_chunk":
        print(chunk.delta_transcript)
