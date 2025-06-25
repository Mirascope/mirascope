import inspect

from mirascope import llm

hardcoded_prompt = [
    llm.messages.system(
        inspect.cleandoc(
            """
            You are a book recommendation agent. Recommend a book to the user based on
            their request; however ensure that the book is age-appropriate for a 13
            year old reader.
            """
        )
    ),
    llm.messages.user("I want to read a fantasy book with music, magic, and dragons!"),
]


def prompt(age: int, genre: str, interests: str) -> list[llm.Message]:
    return [
        llm.messages.system(
            inspect.cleandoc(
                f"""
                You are a book recommendation agent. Recommend a book to the user based on
                their request; however ensure that the book is age-appropriate for a {age}
                year old reader.
                """
            )
        ),
        llm.messages.user(f"I want to read a {genre} book with {interests}!"),
    ]


@llm.prompt(
    """
    [SYSTEM] 
    You are a book recommendation agent. Recommend a book to the user based on
    their request; however ensure that the book is age-appropriate for a {{ age }}
    year old reader.

    [USER]
    I want to read a {{ genre }} book with {{ interests }}!
    """
)
def prompt_from_template(age: int, genre: str, interests: str):
    pass
