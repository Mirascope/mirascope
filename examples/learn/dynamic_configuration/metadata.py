from mirascope.core import openai, prompt_template


@openai.call("gpt-4o-mini")
@prompt_template("Recommend a {genre} book")
def recommend_book(genre: str) -> openai.OpenAIDynamicConfig:
    return {"metadata": {"tags": {f"genre:{genre}", "type:recommendation"}}}


response = recommend_book("horror")
print(response.metadata)
