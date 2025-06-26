from mirascope import llm

recommend_book: llm.Prompt = [llm.messages.user("Recommend a book")]

recommend_fantasy: llm.Prompt = [llm.messages.user("Recommend a fantasy book")]

recommend_scifi: llm.Prompt = [llm.messages.user("Recommend a science fiction book")]


def recommend_genre(genre: str) -> llm.Prompt:
    return [llm.messages.user(f"Recommend a {genre} book")]


@llm.prompt_template("Recommend a {{ genre }} book")
def recommend_genre_from_spec(genre: str): ...
