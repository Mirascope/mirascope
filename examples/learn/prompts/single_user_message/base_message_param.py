from mirascope import BaseMessageParam, prompt_template


@prompt_template()
def recommend_book_prompt(genre: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Recommend a {genre} book")]


print(recommend_book_prompt("fantasy"))
# Output: [BaseMessageParam(role='user', content='Recommend a fantasy book')]
