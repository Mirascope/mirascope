import asyncio

from mirascope import llm


@llm.call("openai:gpt-4o-mini")
async def generate_book_async(genre: str):
    return f"""
    Come up with an imaginary book in genre {genre}. Describe its title and synopsis.

    Generate an image showing the cover of the book.
    Generate an audio clip with a dramatic reading of its opening paragraph.
    """


async def main():
    stream = await generate_book_async.stream("fantasy")

    async for group in stream.groups():
        if group.type == "text":
            async for chunk in group:
                print(chunk.delta, end="", flush=True)
            print()  # New line after text
        
        elif group.type == "image":
            print("Generating image...")
            async for _ in group:
                print(".", end="", flush=True)
            if group.final:
                print(f" ✓ Image complete: {len(group.final.data)} bytes")
        
        elif group.type == "audio":
            print("Generating audio...")
            async for chunk in group:
                if chunk.delta_transcript:
                    print(f"Transcript: {chunk.delta_transcript}")


if __name__ == "__main__":
    asyncio.run(main())