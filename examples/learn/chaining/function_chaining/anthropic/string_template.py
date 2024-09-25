from mirascope.core import anthropic, prompt_template


@anthropic.call("claude-3-5-sonnet-20240620")
@prompt_template("Summarize this text: {text}")
def summarize(text: str): ...


@anthropic.call("claude-3-5-sonnet-20240620")
@prompt_template("Translate this text to {language}: {text}")
def translate(text: str, language: str): ...


summary = summarize("Long English text here...")
translation = translate(summary.content, "french")
print(translation.content)
