from mirascope.core import anthropic, mistral, openai, prompt_template


@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str): ...


openai_recommendation = openai.call("gpt-4o-mini")(recommend_book)("fantasy")
print("OpenAI recommendation:", openai_recommendation.content)

anthropic_recommendation = anthropic.call("claude-3-5-sonnet-20240620")(recommend_book)(
    "fantasy"
)
print("Anthropic recommendation:", anthropic_recommendation.content)

mistral_recommendation = mistral.call("mistral-large-latest")(recommend_book)("fantasy")
print("Mistral recommendation:", mistral_recommendation.content)
