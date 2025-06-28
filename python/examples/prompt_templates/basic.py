from mirascope import llm


@llm.prompt_template(
    """
    [SYSTEM] You are a helpful librarian.
    [USER] Recommend a {{ genre }} book.
    """
)
def spec_prompt_template(genre: str):
    pass


@llm.prompt_template()
def content_prompt_template(genre: str) -> str:
    return f"Recommend a {genre} book"


@llm.prompt_template()
def content_sequence_prompt_template(genre: str) -> list[str]:
    return ["I'm looking for a book.", f"Can you recommend one in {genre}?"]


@llm.prompt_template()
def messages_prompt_template(genre: str) -> list[llm.Message]:
    return [
        llm.messages.system("You are a helpful librarian."),
        llm.messages.user(f"I'm looking for a {genre} book."),
    ]
