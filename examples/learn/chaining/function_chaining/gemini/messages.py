from mirascope.core import Messages, gemini


@gemini.call("gemini-1.5-flash")
def summarize(text: str) -> Messages.Type:
    return Messages.User(f"Summarize this text: {text}")


@gemini.call("gemini-1.5-flash")
def translate(text: str, language: str) -> Messages.Type:
    return Messages.User(f"Translate this text to {language}: {text}")


summary = summarize("Long English text here...")
translation = translate(summary.content, "french")
print(translation.content)
