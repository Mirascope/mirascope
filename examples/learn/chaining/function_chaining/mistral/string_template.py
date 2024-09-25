from mirascope.core import mistral, prompt_template


@mistral.call("mistral-large-latest")
@prompt_template("Summarize this text: {text}")
def summarize(text: str): ...


@mistral.call("mistral-large-latest")
@prompt_template("Translate this text to {language}: {text}")
def translate(text: str, language: str): ...


summary = summarize("Long English text here...")
translation = translate(summary.content, "french")
print(translation.content)
