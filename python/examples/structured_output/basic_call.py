from mirascope import llm


@llm.call("openai/gpt-4o-mini", format=list[str])
def list_books(genre: str):
    return f"List 3 {genre} books."


books = list_books("fantasy").parse()
print(books)
# ['The Name of the Wind', 'Mistborn', 'The Way of Kings']
