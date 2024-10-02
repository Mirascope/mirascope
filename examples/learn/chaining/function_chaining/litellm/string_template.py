from mirascope.core import litellm, prompt_template


@litellm.call("gpt-4o-mini")
@prompt_template("Summarize this text: {text}")
def summarize(text: str): ...


@litellm.call("gpt-4o-mini")
@prompt_template("Translate this text to {language}: {text}")
def translate(text: str, language: str): ...


summary = summarize("Long English text here...")
translation = translate(summary.content, "french")
print(translation.content)
