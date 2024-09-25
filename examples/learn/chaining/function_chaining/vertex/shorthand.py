from mirascope.core import vertex


@vertex.call("gemini-1.5-flash")
def summarize(text: str) -> str:
    return f"Summarize this text: {text}"


@vertex.call("gemini-1.5-flash")
def translate(text: str, language: str) -> str:
    return f"Translate this text to {language}: {text}"


summary = summarize("Long English text here...")
translation = translate(summary.content, "french")
print(translation.content)
