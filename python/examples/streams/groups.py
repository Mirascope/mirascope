from mirascope import llm


@llm.call("openai:gpt-4o-mini")
def generate_book(genre: str):
    return f"""
    Come up with an imaginary book in genre {genre}. Describe its title and synopsis.

    Generate an image showing the cover of the book.
    Generate an audio clip with a dramatic reading of its opening paragraph.
    """


stream = generate_book.stream("fantasy")

print("Processing stream groups:")
for group in stream.groups():
    if group.type == "text":
        print("  Text content:")
        for chunk in group:
            print(chunk.delta, end="", flush=True)
        print()  # Newline after text
        if group.final:
            print(f"  Final text length: {len(group.final.text)} characters")

    elif group.type == "image":
        print("  Image content (progressive render):")
        for _ in group:
            print(".", end="", flush=True)  # Show progress
        if group.final:
            print(
                f"\n  ✓ Image complete ({group.final.mime_type}, {len(group.final.data)} bytes)"
            )

    elif group.type == "audio":
        print("  Audio content (progressive render):")
        for chunk in group:
            if chunk.delta_transcript:
                print(f"  Transcript delta: '{chunk.delta_transcript}'")
        if group.final:
            print(f"  ✓ Audio complete ({group.final.mime_type})")
            if group.final.transcript:
                print(f"  Full transcript: '{group.final.transcript}'")


# Example output (updated to reflect simplification):
# Processing stream groups:
#
#   Text content:
# Embers of the Starfallen is a high fantasy epic...
#   Final text length: 50 characters
#
#   Image content (progressive render):
# ...
#   ✓ Image complete (image/png, 8192 bytes)
#
#   Audio content (progressive render):
#   Transcript delta: 'Embers'
#   Transcript delta: ' of the'
#   ...
#   ✓ Audio complete (audio/wav)
#   Full transcript: 'Embers of the Starfallen'
