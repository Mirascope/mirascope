from mirascope import llm


# Functional Style
def recommend_genre(genre: str):
    return "Recommend a {genre} book"


# Template Style
@llm.prompt("Recommend a {{ genre }} book")
def recommend_genre_template(genre: str): ...
