from mirascope.core import openai, prompt_template


@openai.call("gpt-4o-mini")
@prompt_template()
def summarize(text: str) -> str:
    return f"Summarize this text: {text}"


@openai.call("gpt-4o-mini", output_parser=str)
@prompt_template()
def summarize_and_translate(text: str, language: str) -> str:
    summary = summarize(text)
    return f"Translate this text to {language}: {summary}"


translation = summarize_and_translate("Long English text here...", "French")
print(translation)
