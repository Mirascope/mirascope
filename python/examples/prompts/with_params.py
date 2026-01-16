from mirascope import llm


@llm.prompt
def recommend_book(genre: str):
    return f"Please recommend a book in {genre}."


# Use llm.Model when you need to configure parameters
model = llm.Model("openai/gpt-4o", temperature=0.9)
response = recommend_book(model, "fantasy")
print(response.pretty())
