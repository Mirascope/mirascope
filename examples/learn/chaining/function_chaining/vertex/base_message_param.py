from mirascope.core import BaseMessageParam, vertex


@vertex.call("gemini-1.5-flash")
def summarize(text: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Summarize this text: {text}")]


@vertex.call("gemini-1.5-flash")
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
