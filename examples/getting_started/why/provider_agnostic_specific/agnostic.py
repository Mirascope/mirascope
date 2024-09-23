from mirascope.core import anthropic, openai, prompt_template


@prompt_template()
def recommend_book(genre: str) -> str:
    return f"Recommend a {genre} book"


openai_recommend_book = openai.call("gpt-4o-mini")(recommend_book)
openai_response = openai_recommend_book("fantasy")
print(openai_response.content)

anthropic_recommend_book = anthropic.call("claude-3-5-sonnet-20240620")(recommend_book)
anthropic_response = anthropic_recommend_book("fantasy")
print(anthropic_response.content)
