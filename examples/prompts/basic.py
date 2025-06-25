from mirascope import llm


@llm.prompt(
    """
    [SYSTEM] You are a helpful librarian.
    [USER] Recommend a {{ genre }} book.
    """
)
def template_prompt(genre: str):
    pass


@llm.prompt()
def content_prompt(genre: str) -> str:
    return f"Recommend a {genre} book"


@llm.prompt()
def content_sequence_prompt(genre: str) -> list[str]:
    return ["I'm looking for a book.", f"Can you recommend one in {genre}"]


@llm.prompt()
def messages_prompt(genre: str) -> list[llm.Message]:
    return [
        llm.messages.system("You are a helpful librarian."),
        llm.messages.user(f"I'm looking for a ${genre} book."),
    ]
