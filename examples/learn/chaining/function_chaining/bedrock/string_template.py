from mirascope.core import bedrock, prompt_template


@bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
@prompt_template("Summarize this text: {text}")
def summarize(text: str): ...


@bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
@prompt_template("Translate this text to {language}: {text}")
def translate(text: str, language: str): ...


summary = summarize("Long English text here...")
translation = translate(summary.content, "french")
print(translation.content)
