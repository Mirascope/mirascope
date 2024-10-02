from mirascope.core import mistral


@mistral.call("mistral-large-latest")
def summarize(text: str) -> str:
    return f"Summarize this text: {text}"


@mistral.call("mistral-large-latest")
def translate(text: str, language: str) -> str:
    return f"Translate this text to {language}: {text}"


summary = summarize("Long English text here...")
translation = translate(summary.content, "french")
print(translation.content)
