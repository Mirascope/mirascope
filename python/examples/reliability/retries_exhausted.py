from mirascope import llm

model = llm.retry_model(
    "openai/gpt-4o-mini",
    max_retries=2,
    fallback_models=["anthropic/claude-3-5-haiku-latest"],
)

try:
    response = model.call("Recommend a fantasy book")
    print(response.text())
except llm.RetriesExhausted as e:
    print(f"All {len(e.failures)} attempts failed:")
    for failure in e.failures:
        print(f"  {failure.model.model_id}: {type(failure.exception).__name__}")
