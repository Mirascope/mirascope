from mirascope import llm

hardcoded_prompt = [llm.messages.user("Please recommend a book")]

fantasy_prompt = [llm.messages.user("Please recommend a fantasy book")]

scifi_prompt = [llm.messages.user("Please recommend a science fiction book")]


def genre_prompt(genre: str) -> list[llm.Message]:
    return [llm.messages.user(f"Please recommend a {genre} book")]


# Template Style
@llm.prompt("Please recommend a {{ genre }} book")
def genre_prompt_from_template(genre: str):
    pass


# Functional Style
@llm.prompt()
def genre_prompt_functional(genre: str) -> str:
    return f"Please recommend a {genre} book"
