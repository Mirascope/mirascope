from mirascope.core import google


@google.call("gemini-1.5-flash")
def summarize(text: str) -> str:
    return f"Summarize this text: {text}"


@google.call("gemini-1.5-flash")
def translate(text: str, language: str) -> str:
    return f"Translate this text to {language}: {text}"


summary = summarize("Long English text here...")
translation = translate(summary.content, "french")
print(translation.content)
