from mirascope.core import azure, prompt_template


@azure.call("gpt-4o-mini")
@prompt_template("Summarize this text: {text}")
def summarize(text: str): ...


@azure.call("gpt-4o-mini")
@prompt_template("Translate this text to {language}: {text}")
def translate(text: str, language: str): ...


summary = summarize("Long English text here...")
translation = translate(summary.content, "french")
print(translation.content)
