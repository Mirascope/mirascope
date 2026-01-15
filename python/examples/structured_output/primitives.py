from mirascope import llm


@llm.call("openai/gpt-4o-mini", format=dict[str, str])
def recommend_books(genres: list[str]):
    return f"Recommend a book for each of the following genres: {', '.join(genres)}"


recommendations = recommend_books(["scifi", "fantasy", "romantasy"]).parse()
print(recommendations)
# {'scifi': 'Dune', 'fantasy': 'The Name of the Wind', 'romantasy': 'A Court of Thorns and Roses'}
