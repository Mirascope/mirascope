from mirascope.core import groq, prompt_template


@groq.call("llama-3.1-70b-versatile")
@prompt_template("Summarize this text: {text}")
def summarize(text: str): ...


@groq.call("llama-3.1-70b-versatile")
@prompt_template("Translate this text to {language}: {text}")
def translate(text: str, language: str): ...


summary = summarize("Long English text here...")
translation = translate(summary.content, "french")
print(translation.content)
