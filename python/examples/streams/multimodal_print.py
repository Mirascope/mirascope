from mirascope import llm


@llm.call("openai:gpt-4o-mini")
def generate_book(genre: str):
    return f"""
    Come up with an imaginary book in genre {genre}.
    Provide its title and author, and then generate a book cover for it.
    """


stream = generate_book.stream("fantasy")

for chunk in stream:
    print(chunk)

# Output:
# Sure, I can generate a fictional book for you.
# Embers of the Starfallen is a high fantasy fiction book by Lyra Nightward.
# {image:start}....{image:done}
# Here is its generated cover.
