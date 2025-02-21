from mirascope import prompt_template


@prompt_template("Recommend a {genre} book")
def recommend_book_prompt(genre: str): ...


print(recommend_book_prompt("fantasy"))
# Output: [BaseMessageParam(role='user', content='Recommend a fantasy book')]
