from mirascope.core import BaseDynamicConfig, mistral, prompt_template


@mistral.call("mistral-large-latest")
@prompt_template("Summarize this text: {text}")
def summarize(text: str): ...


@mistral.call("mistral-large-latest")
@prompt_template("Translate this text to {language}: {summary}")
def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
    return {"computed_fields": {"summary": summarize(text)}}


response = summarize_and_translate("Long English text here...", "french")
print(response.content)
