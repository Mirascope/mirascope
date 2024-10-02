from mirascope.core import litellm


@litellm.call("gpt-4o-mini")
def summarize(text: str) -> str:
    return f"Summarize this text: {text}"


@litellm.call("gpt-4o-mini")
def translate(text: str, language: str) -> str:
    return f"Translate this text to {language}: {text}"


summary = summarize("Long English text here...")
translation = translate(summary.content, "french")
print(translation.content)
