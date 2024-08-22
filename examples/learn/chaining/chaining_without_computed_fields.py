from typing import Any

from mirascope.core import openai, prompt_template


@openai.call(model="gpt-3.5-turbo")
@prompt_template("Summarize this text: {text}")
def summarize(text: str) -> None: ...


@openai.call(model="gpt-3.5-turbo")
@prompt_template("Translate this text to {language}: {summary}")
def translate(summary: str, language: str) -> None: ...


def summarize_and_translate(original_text: str) -> Any:  # noqa: ANN401
    summary = summarize(original_text)
    translation = translate(summary.content, "french")
    return translation.content
