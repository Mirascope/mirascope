from mirascope.core import openai, prompt_template
from openai import OpenAI

client = OpenAI()


def summarize(text: str) -> str:
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Summarize this text: {text}"}],
    )
    return str(completion.choices[0].message.content)


@openai.call("gpt-4o-mini")
@prompt_template()
def translate(summary: str, language: str) -> str:
    return f"Translate this text to {language}: {summary}"


def summarize_and_translate(text: str, language: str) -> str:
    summary = summarize(text)
    translation = translate(summary, language)
    return translation.content


translation = summarize_and_translate("Long English text here...", "French")
print(translation)
