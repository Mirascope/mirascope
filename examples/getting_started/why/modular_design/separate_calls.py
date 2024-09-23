from mirascope.core import openai, prompt_template


@openai.call("gpt-4o-mini")
@prompt_template()
def summarize(text: str) -> str:
    return f"Summarize this text: {text}"


@openai.call("gpt-4o-mini")
@prompt_template()
def translate(summary: str, language: str) -> str:
    return f"Translate this text to {language}: {summary}"


def summarize_and_translate(text: str, language: str) -> str:
    summary = summarize(text)
    translation = translate(summary.content, language)
    return translation.content


translation = summarize_and_translate("Long English text here...", "French")
print(translation)
