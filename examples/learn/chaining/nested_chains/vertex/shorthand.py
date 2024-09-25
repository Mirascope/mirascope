from mirascope.core import vertex


@vertex.call("gemini-1.5-flash")
def summarize(text: str) -> str:
    return f"Summarize this text: {text}"


@vertex.call("gemini-1.5-flash")
def summarize_and_translate(text: str, language: str) -> str:
    summary = summarize(text)
    return f"Translate this text to {language}: {summary.content}"


response = summarize_and_translate("Long English text here...", "french")
print(response.content)
