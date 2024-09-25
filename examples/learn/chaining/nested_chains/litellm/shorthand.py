from mirascope.core import litellm


@litellm.call("gpt-4o-mini")
def summarize(text: str) -> str:
    return f"Summarize this text: {text}"


@litellm.call("gpt-4o-mini")
def summarize_and_translate(text: str, language: str) -> str:
    summary = summarize(text)
    return f"Translate this text to {language}: {summary.content}"


response = summarize_and_translate("Long English text here...", "french")
print(response.content)
