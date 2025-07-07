from mirascope import llm


@llm.call("openai:gpt-4o-mini")
def generate_book(genre: str):
    return f"""
    Come up with an imaginary book in genre {genre}. Describe its title and synopsis.

    Generate an image showing the cover of the book.
    Generate an audio clip with a dramatic reading of its opening paragraph.
    """


stream = generate_book.stream("fantasy")

for group in stream.groups():
    if group.type == "text":
        for chunk in group:
            print(chunk.delta, end="", flush=True)

    elif group.type == "image":
        print("Processing image content:")
        for _ in group:
            print("  Image chunk received (progressive render)")
            print(f"  Current image size: ~{len(group.partial.delta)} bytes")

        if group.final:
            print(
                f"✓ Completed image: {group.final.mime_type}, ~{len(group.final.data)} bytes"
            )

    elif group.type == "audio":
        print("Processing audio content:")
        for chunk in group:
            if chunk.delta_transcript:
                print(f"  Transcript: '{chunk.delta_transcript}'")
            print(f". Current audio size: ~{len(group.partial.delta)} bytes")

        if group.final:
            print(f"✓ Completed audio: {group.final.mime_type}")
            if group.final.transcript:
                print(f"  Full transcript: '{group.final.transcript}'")

    print()  # Blank line between groups


# Example output:
# Processing text content:
#   Text chunk: 'Embers'
#   Accumulated so far: 'Embers...'
#   Text chunk: ' of the'
#   Accumulated so far: 'Embers of the...'
#   ...
# ✓ Completed text: Text
#   Final text: 'Embers of the Starfallen is a high fantasy epic...'
#
# Processing image content:
#   Image chunk received (progressive render)
#   Current image size: ~1024 bytes
#   Image chunk received (progressive render)
#   Current image size: ~2048 bytes
#   ...
# ✓ Completed image: Image
#   Final image: image/png, ~8192 bytes
#
# Processing audio content:
#   Audio chunk received
#   Transcript: 'Embers'
#   Full transcript so far: 'Embers'
#   Audio chunk received
#   Transcript: ' of the'
#   Full transcript so far: 'Embers of the'
#   ...
# ✓ Completed audio: Audio
#   Final audio: audio/wav
#   Full transcript: 'Embers of the Starfallen'
