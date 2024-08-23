from mirascope.core import openai, prompt_template


@openai.call(model="gpt-3.5-turbo")
@prompt_template("Summarize this text: {text}")
def summarize(text: str): ...


@openai.call(model="gpt-3.5-turbo")
@prompt_template("Translate this text to {language}: {summary}")
def summarize_and_translate(text: str, language: str) -> openai.OpenAIDynamicConfig:
    return {"computed_fields": {"summary": summarize(text)}}


response = summarize_and_translate("Long English text here...", "french")
print(response.content)
print(
    response.model_dump()["computed_fields"]
)  # This will contain the `summarize` response
