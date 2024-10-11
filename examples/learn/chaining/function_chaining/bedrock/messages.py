from mirascope.core import Messages, bedrock


@bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
def summarize(text: str) -> Messages.Type:
    return Messages.User(f"Summarize this text: {text}")


@bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
def translate(text: str, language: str) -> Messages.Type:
    return Messages.User(f"Translate this text to {language}: {text}")


summary = summarize("Long English text here...")
translation = translate(summary.content, "french")
print(translation.content)
