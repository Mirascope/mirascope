from mirascope import BaseDynamicConfig, BaseMessageParam, llm


@llm.call(provider="openai", model="gpt-4o-mini")
def summarize(text: str) -> str:
    return f"Summarize this text: {text}"


@llm.call(provider="openai", model="gpt-4o-mini")
def summarize_and_translate(text: str, language: str) -> BaseDynamicConfig:
    summary = summarize(text)
    return {
        "messages": [
            BaseMessageParam(
                role="user",
                content=f"Translate this text to {language}: {summary.content}",
            )
        ],
        "computed_fields": {"summary": summary},
    }


response = summarize_and_translate("Long English text here...", "french")
print(response.content)
print(
    response.model_dump()["computed_fields"]
)  # This will contain the `summarize` response
