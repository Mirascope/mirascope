from mirascope.core import BaseMessageParam, bedrock


@bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
def summarize(text: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Summarize this text: {text}")]


@bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
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
