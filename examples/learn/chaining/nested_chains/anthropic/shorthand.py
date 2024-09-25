from mirascope.core import anthropic


@anthropic.call("claude-3-5-sonnet-20240620")
def summarize(text: str) -> str:
    return f"Summarize this text: {text}"


@anthropic.call("claude-3-5-sonnet-20240620")
def summarize_and_translate(text: str, language: str) -> str:
    summary = summarize(text)
    return f"Translate this text to {language}: {summary.content}"


response = summarize_and_translate("Long English text here...", "french")
print(response.content)
