from mirascope import llm


@llm.prompt(format=list[str])
def list_books(genre: str):
    return f"List 3 {genre} books."


books = list_books("openai/gpt-4o-mini", "fantasy").parse()
print(books)
# ['The Name of the Wind', 'Mistborn', 'The Way of Kings']
