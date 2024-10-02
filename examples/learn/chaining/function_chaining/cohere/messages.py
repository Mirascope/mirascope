from mirascope.core import Messages, cohere


@cohere.call("command-r-plus")
def summarize(text: str) -> Messages.Type:
    return Messages.User(f"Summarize this text: {text}")


@cohere.call("command-r-plus")
def translate(text: str, language: str) -> Messages.Type:
    return Messages.User(f"Translate this text to {language}: {text}")


summary = summarize("Long English text here...")
translation = translate(summary.content, "french")
print(translation.content)
