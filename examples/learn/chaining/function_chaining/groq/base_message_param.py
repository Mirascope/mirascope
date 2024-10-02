from mirascope.core import BaseMessageParam, groq


@groq.call("llama-3.1-70b-versatile")
def summarize(text: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Summarize this text: {text}")]


@groq.call("llama-3.1-70b-versatile")
def translate(text: str, language: str) -> list[BaseMessageParam]:
    return [
        BaseMessageParam(
            role="user",
            content=f"Translate this text to {language}: {text}",
        )
    ]


summary = summarize("Long English text here...")
translation = translate(summary.content, "french")
print(translation.content)
