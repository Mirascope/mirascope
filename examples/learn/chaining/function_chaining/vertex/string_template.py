from mirascope.core import prompt_template, vertex


@vertex.call("gemini-1.5-flash")
@prompt_template("Summarize this text: {text}")
def summarize(text: str): ...


@vertex.call("gemini-1.5-flash")
@prompt_template("Translate this text to {language}: {text}")
def translate(text: str, language: str): ...


summary = summarize("Long English text here...")
translation = translate(summary.content, "french")
print(translation.content)
