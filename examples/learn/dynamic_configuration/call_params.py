from mirascope.core import openai, prompt_template


@openai.call("gpt-4o-mini")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str, creativity: float) -> openai.OpenAIDynamicConfig:
    return {"call_params": {"temperature": creativity}}


response = recommend_book("mystery", 0.8)
print(response.content)
