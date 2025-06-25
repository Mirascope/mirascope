from mirascope import llm

recommend_book_prompt = [llm.messages.user("Please recommend a book")]

recommend_fantasy_prompt = [llm.messages.user("Please recommend a fantasy book")]

recommend_scifi_prompt = [llm.messages.user("Please recommend a science fiction book")]


def recommend_genre_prompt(genre: str) -> list[llm.Message]:
    return [llm.messages.user(f"Please recommend a {genre} book")]


# Template Style
@llm.prompt("Please recommend a {{ genre }} book")
def recommend_genre_prompt_template(genre: str): ...


# Functional Style
@llm.prompt()
def recommend_genre_prompt_functional(genre: str) -> str:
    return f"Please recommend a {genre} book"
