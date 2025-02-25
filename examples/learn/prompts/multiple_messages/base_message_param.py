from mirascope import BaseMessageParam, prompt_template


@prompt_template()
def recommend_book_prompt(genre: str) -> list[BaseMessageParam]:
    return [
        BaseMessageParam(role="system", content="You are a librarian"),
        BaseMessageParam(role="user", content=f"Recommend a {genre} book"),
    ]


print(recommend_book_prompt("fantasy"))
# Output: [
#   BaseMessageParam(role='system', content='You are a librarian'),
#   BaseMessageParam(role='user', content='Recommend a fantasy book'),
# ]
