from mirascope.core import BaseDynamicConfig, groq, prompt_template


@groq.call("llama-3.1-70b-versatile")
@prompt_template("Summarize this text: {text}")
def summarize(text: str): ...


@groq.call("llama-3.1-70b-versatile")
@prompt_template("Translate this text to {language}: {summary}")
def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
    return {"computed_fields": {"summary": summarize(text)}}


response = summarize_and_translate("Long English text here...", "french")
print(response.content)
print(
    response.model_dump()["computed_fields"]
)  # This will contain the `summarize` response
