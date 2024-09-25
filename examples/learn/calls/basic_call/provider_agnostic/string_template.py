from mirascope.core import anthropic, openai, prompt_template


@prompt_template("Recommend a {genre} book")
def recommend_book_prompt(genre: str): ...


# OpenAI
openai_model = "gpt-4o-mini"
openai_recommend_book = openai.call(openai_model)(recommend_book_prompt)
openai_response = openai_recommend_book("fantasy")
print(openai_response.content)

# Anthropic
anthropic_model = "claude-3-5-sonnet-20240620"
anthropic_recommend_book = anthropic.call(anthropic_model)(recommend_book_prompt)
anthropic_response = anthropic_recommend_book("fantasy")
print(anthropic_response.content)
