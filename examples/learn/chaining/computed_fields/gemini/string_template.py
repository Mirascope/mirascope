from mirascope.core import BaseDynamicConfig, gemini, prompt_template


@gemini.call("gemini-1.5-flash")
@prompt_template("Summarize this text: {text}")
def summarize(text: str): ...


@gemini.call("gemini-1.5-flash")
@prompt_template("Translate this text to {language}: {summary}")
def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
    return {"computed_fields": {"summary": summarize(text)}}


response = summarize_and_translate("Long English text here...", "french")
print(response.content)
print(
    response.model_dump()["computed_fields"]
)  # This will contain the `summarize` response
