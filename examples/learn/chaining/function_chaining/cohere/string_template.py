from mirascope.core import cohere, prompt_template


@cohere.call("command-r-plus")
@prompt_template("Summarize this text: {text}")
def summarize(text: str): ...


@cohere.call("command-r-plus")
@prompt_template("Translate this text to {language}: {text}")
def translate(text: str, language: str): ...


summary = summarize("Long English text here...")
translation = translate(summary.content, "french")
print(translation.content)
