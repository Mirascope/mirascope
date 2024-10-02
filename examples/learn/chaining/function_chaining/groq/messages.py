from mirascope.core import Messages, groq


@groq.call("llama-3.1-70b-versatile")
def summarize(text: str) -> Messages.Type:
    return Messages.User(f"Summarize this text: {text}")


@groq.call("llama-3.1-70b-versatile")
def translate(text: str, language: str) -> Messages.Type:
    return Messages.User(f"Translate this text to {language}: {text}")


summary = summarize("Long English text here...")
translation = translate(summary.content, "french")
print(translation.content)
