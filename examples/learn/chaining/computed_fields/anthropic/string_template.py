from mirascope.core import BaseDynamicConfig, anthropic, prompt_template


@anthropic.call("claude-3-5-sonnet-20240620")
@prompt_template("Summarize this text: {text}")
def summarize(text: str): ...


@anthropic.call("claude-3-5-sonnet-20240620")
@prompt_template("Translate this text to {language}: {summary}")
def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
    return {"computed_fields": {"summary": summarize(text)}}


response = summarize_and_translate("Long English text here...", "french")
print(response.content)
print(
    response.model_dump()["computed_fields"]
)  # This will contain the `summarize` response
