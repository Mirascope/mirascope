from mirascope.core import bedrock


@bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
def summarize(text: str) -> str:
    return f"Summarize this text: {text}"


@bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
def summarize_and_translate(text: str, language: str) -> str:
    summary = summarize(text)
    return f"Translate this text to {language}: {summary.content}"


response = summarize_and_translate("Long English text here...", "french")
print(response.content)
