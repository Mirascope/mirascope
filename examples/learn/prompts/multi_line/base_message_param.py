import inspect

from mirascope import BaseMessageParam, prompt_template


@prompt_template()
def recommend_book_prompt(genre: str) -> list[BaseMessageParam]:
    return [
        BaseMessageParam(
            role="user",
            content=inspect.cleandoc(
                f"""
                Recommend a {genre} book.
                Output in the format Title by Author.
                """
            ),
        ),
    ]


print(recommend_book_prompt("fantasy"))
# Output: [BaseMessageParam(role='system', content='Recommend a fantasy book.\nOutput in the format Title by Author.')]
