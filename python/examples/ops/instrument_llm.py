from mirascope import llm, ops

# Configure Mirascope Cloud
ops.configure()

# Enable automatic LLM instrumentation for Gen AI spans
ops.instrument_llm()

# Now all Model calls are automatically traced with Gen AI semantic conventions
model = llm.model("openai/gpt-4o-mini")
response = model.call("What is the capital of France?")
print(response.text())

# Disable instrumentation when done
ops.uninstrument_llm()
