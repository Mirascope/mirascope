from mirascope.core import BaseDynamicConfig, Messages, vertex


@vertex.call("gemini-1.5-flash")
def summarize(text: str) -> str:
    return f"Summarize this text: {text}"


@vertex.call("gemini-1.5-flash")
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
