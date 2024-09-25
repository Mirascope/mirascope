from mirascope.core import BaseDynamicConfig, Messages, anthropic


@anthropic.call("claude-3-5-sonnet-20240620")
def summarize(text: str) -> str:
    return f"Summarize this text: {text}"


@anthropic.call("claude-3-5-sonnet-20240620")
def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
    summary = summarize(text)
    return {
        "messages": [
            Messages.User(f"Translate this text to {language}: {summary.content}")
        ],
        "computed_fields": {"summary": summary},
    }


response = summarize_and_translate("Long English text here...", "french")
print(response.content)
print(
    response.model_dump()["computed_fields"]
)  # This will contain the `summarize` response
