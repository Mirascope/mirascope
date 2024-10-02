from mirascope.core import cohere


@cohere.call("command-r-plus")
def summarize(text: str) -> str:
    return f"Summarize this text: {text}"


@cohere.call("command-r-plus")
def translate(text: str, language: str) -> str:
    return f"Translate this text to {language}: {text}"


summary = summarize("Long English text here...")
translation = translate(summary.content, "french")
print(translation.content)
