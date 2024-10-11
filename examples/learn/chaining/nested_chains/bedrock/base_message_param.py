from mirascope.core import BaseMessageParam, bedrock


@bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
def summarize(text: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Summarize this text: {text}")]


@bedrock.call("anthropic.claude-3-haiku-20240307-v1:0")
def summarize_and_translate(text: str, language: str) -> list[BaseMessageParam]:
    summary = summarize(text)
    return [
        BaseMessageParam(
            role="user",
            content=f"Translate this text to {language}: {summary.content}",
        )
    ]


response = summarize_and_translate("Long English text here...", "french")
print(response.content)
