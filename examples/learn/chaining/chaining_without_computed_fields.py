from mirascope.core import openai, prompt_template


@openai.call(model="gpt-3.5-turbo")
@prompt_template("Summarize this text: {text}")
def summarize(text: str): ...


@openai.call(model="gpt-3.5-turbo")
@prompt_template("Translate this text to {language}: {summary}")
def translate(summary: str, language: str): ...


def summarize_and_translate(original_text: str):
    summary = summarize(original_text)
    translation = translate(summary.content, "french")
    return translation.content
