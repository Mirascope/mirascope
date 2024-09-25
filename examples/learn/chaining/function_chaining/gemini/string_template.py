from mirascope.core import gemini, prompt_template


@gemini.call("gemini-1.5-flash")
@prompt_template("Summarize this text: {text}")
def summarize(text: str): ...


@gemini.call("gemini-1.5-flash")
@prompt_template("Translate this text to {language}: {text}")
def translate(text: str, language: str): ...


summary = summarize("Long English text here...")
translation = translate(summary.content, "french")
print(translation.content)
