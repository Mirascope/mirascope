from mirascope import Messages, prompt_template


@prompt_template()
def recommend_book_prompt(genre: str) -> Messages.Type:
    return [
        Messages.System("You are a librarian"),
        Messages.User(f"Recommend a {genre} book"),
    ]


print(recommend_book_prompt("fantasy"))
# Output: [
#   BaseMessageParam(role='system', content='You are a librarian'),
#   BaseMessageParam(role='user', content='Recommend a fantasy book'),
# ]
