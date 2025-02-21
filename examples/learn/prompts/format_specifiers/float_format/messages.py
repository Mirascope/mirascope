from mirascope import Messages, prompt_template


@prompt_template()
def recommend_book(genre: str, price: float) -> Messages.Type:
    return Messages.User(f"Recommend a {genre} book under ${price:.2f}")


print(recommend_book("fantasy", 12.3456))
# Output: [BaseMessageParam(role='user', content='Recommend a fantasy book under $12.35')]
