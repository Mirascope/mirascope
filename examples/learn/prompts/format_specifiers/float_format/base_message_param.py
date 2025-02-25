from mirascope import BaseMessageParam, prompt_template


@prompt_template()
def recommend_book(genre: str, price: float) -> list[BaseMessageParam]:
    return [
        BaseMessageParam(
            role="user", content=f"Recommend a {genre} book under ${price:.2f}"
        )
    ]


print(recommend_book("fantasy", 12.3456))
# Output: [BaseMessageParam(role='user', content='Recommend a fantasy book under $12.35')]
