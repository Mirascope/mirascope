from mirascope import llm

model = llm.retry_model(
    "openai/gpt-4o-mini",
    fallback_models=[
        "anthropic/claude-3-5-haiku-latest",
        "google/gemini-2.0-flash",
    ],
)
response = model.call("Recommend a fantasy book")
print(response.text())
# > The Name of the Wind by Patrick Rothfuss
