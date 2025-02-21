import inspect

from mirascope import Messages, prompt_template


@prompt_template()
def recommend_book_prompt(genre: str) -> Messages.Type:
    return Messages.User(
        inspect.cleandoc(
            f"""
            Recommend a {genre} book.
            Output in the format Title by Author.
            """
        )
    )


print(recommend_book_prompt("fantasy"))
# Output: [BaseMessageParam(role='system', content='Recommend a fantasy book.\nOutput in the format Title by Author.')]
