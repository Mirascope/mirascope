from mirascope.core import BaseMessageParam, anthropic


@anthropic.call("claude-3-5-sonnet-20240620")
def summarize(text: str) -> list[BaseMessageParam]:
    return [BaseMessageParam(role="user", content=f"Summarize this text: {text}")]


@anthropic.call("claude-3-5-sonnet-20240620")
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
