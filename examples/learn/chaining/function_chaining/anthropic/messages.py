from mirascope.core import Messages, anthropic


@anthropic.call("claude-3-5-sonnet-20240620")
def summarize(text: str) -> Messages.Type:
    return Messages.User(f"Summarize this text: {text}")


@anthropic.call("claude-3-5-sonnet-20240620")
def translate(text: str, language: str) -> Messages.Type:
    return Messages.User(f"Translate this text to {language}: {text}")


summary = summarize("Long English text here...")
translation = translate(summary.content, "french")
print(translation.content)
