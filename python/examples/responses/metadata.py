from mirascope import llm

model = llm.model("openai/gpt-5-mini")
response = model.call("Hello!")

# Response metadata
print(f"Provider: {response.provider_id}")
print(f"Model: {response.model_id}")
print(f"Params: {response.params}")

# Access the raw provider response if needed
print(f"Raw response type: {type(response.raw)}")
