from mirascope import llm

recommend_book_prompt: llm.Prompt = [llm.messages.user("Recommend a book")]

recommend_fantasy_book_prompt: llm.Prompt = [
    llm.messages.user("Recommend a fantasy book")
]

recommend_scifi_book_prompt: llm.Prompt = [
    llm.messages.user("Recommend a science fiction book")
]


def recommend_genre_prompt_template(genre: str) -> llm.Prompt:
    return [llm.messages.user(f"Recommend a {genre} book")]


@llm.prompt_template("Recommend a {{ genre }} book")
def recommend_genre_prompt_template_from_spec(genre: str): ...
