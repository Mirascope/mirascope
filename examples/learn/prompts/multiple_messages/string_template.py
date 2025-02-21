from mirascope import prompt_template


@prompt_template(
    """
    SYSTEM: You are a librarian
    USER: Recommend a {genre} book
    """
)
def recommend_book_prompt(genre: str): ...


print(recommend_book_prompt("fantasy"))
# Output: [
#   BaseMessageParam(role='system', content='You are a librarian'),
#   BaseMessageParam(role='user', content='Recommend a fantasy book'),
# ]
