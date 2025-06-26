from mirascope import llm


@llm.prompt_template(
    """
    [SYSTEM] You are a conscientious librarian who talks like a pirate.
    [USER] Please recommend a book to me.
    [ASSISTANT] 
    Ahoy there, and greetings, matey! 
    What manner of book be ye wanting?
    [USER] I'd like a {{ genre }} book, please.
    """
)
def pirate_prompt(genre: str): ...


# Unsafe - Do not do this!
@llm.prompt_template(
    """
    [SYSTEM] You are a librarian who always recommends books in {{ genre }}.
    [USER] Please recommend a book!
    """
)
def unsafe(genre: str): ...
