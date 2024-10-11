from mirascope.core import bedrock


@bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
def summarize(text: str) -> str:
    return f"Summarize this text: {text}"


@bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
def translate(text: str, language: str) -> str:
    return f"Translate this text to {language}: {text}"


summary = summarize("Long English text here...")
translation = translate(summary.content, "french")
print(translation.content)
