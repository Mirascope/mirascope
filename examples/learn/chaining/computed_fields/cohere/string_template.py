from mirascope.core import BaseDynamicConfig, cohere, prompt_template


@cohere.call("command-r-plus")
@prompt_template("Summarize this text: {text}")
def summarize(text: str): ...


@cohere.call("command-r-plus")
@prompt_template("Translate this text to {language}: {summary}")
def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
    return {"computed_fields": {"summary": summarize(text)}}


response = summarize_and_translate("Long English text here...", "french")
print(response.content)
print(
    response.model_dump()["computed_fields"]
)  # This will contain the `summarize` response
