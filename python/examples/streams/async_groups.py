import asyncio

from mirascope import llm


@llm.call("openai:gpt-4o-mini")
def generate_book(genre: str):
    return f"""
    Come up with an imaginary book in genre {genre}. Describe its title and synopsis.

    Generate an image showing the cover of the book.
    Generate an audio clip with a dramatic reading of its opening paragraph.
    """


async def main():
    stream = generate_book.stream_async("fantasy")

    async for group in stream.groups():
        if group.type == "text":
            async for chunk in group:
                print(chunk, end="", flush=True)
            print("")  # New line after text

        elif group.type == "image":
            print("Generating image...")
            async for _ in group:
                print(".", end="", flush=True)
            final = await group.collect()
            print(f" ✓ Image complete: {len(final.data)} bytes")

        elif group.type == "audio":
            print("Generating audio...")
            async for chunk in group:
                if chunk.delta_transcript:
                    print(f"Transcript: {chunk.delta_transcript}")


if __name__ == "__main__":
    asyncio.run(main())
