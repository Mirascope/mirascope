from mirascope import prompt_template


@prompt_template(
    """
    Recommend a {genre} book.
    Output in the format Title by Author.
    """
)
def recommend_book_prompt(genre: str): ...


print(recommend_book_prompt("fantasy"))
# Output: [BaseMessageParam(role='system', content='Recommend a fantasy book.\nOutput in the format Title by Author.')]
