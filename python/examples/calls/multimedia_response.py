from mirascope import llm


@llm.call("openai:gpt-4o-mini")
def generate_book(genre: str):
    return f"""
    Come up with an imaginary book in genre {genre}. Describe its title and synopsis.

    If you have image capabilities, produce an image showing a cover of the book.

    If you have audio capabilities, produce an audio clip with a dramatic reading of the
    title. If not, generate an xml document with a SSML snippet that would produce such a reading.
    """


book: llm.Response = generate_book("fantasy")
print(book)
# > {thinking: thoughts="The user wants an imaginary fantasy book...""}
# > Embers of the Starfallen is a high fantasy epic by Lyra Nightwind, featuring...
# > {image: url="https://sdmntprcentralus.oaiusercontent.com/files/...""}
# > Here's an SSML snippet you can feed into any compatible Text-to-Speech engine...
# > {document type="xml"}
# ...

for content_item in book.content:
    if isinstance(content_item, str):
        print(f"Text: {content_item}")
    elif isinstance(content_item, llm.Tool):
        print(f"Tool call: {content_item.name}")
    else:
        print(f"Content type: {content_item.type}")


# Would print:
# > Content type: thinking
# > Text: Embers of the Starfallen is a high fantasy epic...
# > Content type: image
# > Text: Here's an SSM snippet...
# > Content type: document

# Access specific content types
if book.image:
    print(f"Image data: {book.image.data[:50]}...")  # First 50 chars of base64 data
    print(f"Image type: {book.image.mime_type}")
    # Would print:
    # > Image data: iVBORw0KGgoAAAANSUhEUgAABQAAAAMACAYAAADpLHQ3AAAA...
    # > Image type: image/png

if book.audio:
    print(f"Audio data: {book.audio.data}")
    if book.audio.transcript:
        print(f"Transcript: {book.audio.transcript}")
