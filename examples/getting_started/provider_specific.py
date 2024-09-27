from mirascope.core import anthropic, openai


@openai.call("gpt-4o-mini")
def openai_recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


@anthropic.call("claude-3-5-sonnet-20240620")
def anthropic_recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


openai_response = openai_recommend_book("fantasy")
print(openai_response.content)

anthropic_response = anthropic_recommend_book("fantasy")
print(anthropic_response.content)
