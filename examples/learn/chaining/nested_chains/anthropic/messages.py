from mirascope.core import Messages, anthropic


@anthropic.call("claude-3-5-sonnet-20240620")
def summarize(text: str) -> Messages.Type:
    return Messages.User(f"Summarize this text: {text}")


@anthropic.call("claude-3-5-sonnet-20240620")
def summarize_and_translate(text: str, language: str) -> Messages.Type:
    summary = summarize(text)
    return Messages.User(f"Translate this text to {language}: {summary.content}")


response = summarize_and_translate("Long English text here...", "french")
print(response.content)
